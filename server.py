import sys
sys.path.append('tornado')
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.template
import os
import crosspurposes.game
import kaibosh.game
from cardgame.deck import Suits, Values
import traceback

loader = tornado.template.Loader(os.path.join(os.path.join(
    os.path.realpath(__file__) + '/../'), 'templates'))

game_factories = {
    'kaibosh': kaibosh.game.KaiboshGame,
    'crosspurposes': crosspurposes.game.CrossPurposesGame
}

games = []
users = {}


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
            return self.get_secure_cookie("user")


class LoginHandler(BaseHandler):

    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        if self.get_argument('name') not in users:
            users[self.get_argument('name')] = {}
            LobbyWebSocket.update()
        self.redirect("/")


class LogoutHandler(BaseHandler):

    def get(self):
        self.set_secure_cookie("user", "")
        self.redirect('/')


class QuitHandler(BaseHandler):

    def get(self):
        user = users[self.get_current_user()]
        user['player'].left = True
        del user['player']
        del user['game']
        self.redirect('/')
        LobbyWebSocket.update()


class LobbyHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        if self.get_current_user() not in users:
            self.redirect('/logout')
            return
        user = self.get_current_user()
        if 'game' in users[user]:
            game = users[user]['game']
            player = users[user]['player']
            self.redirect('/' + str(id(game)) + '/' + str(id(player)))
            return
        self.write(loader.load('lobby.html').generate(
            user=user,
            games=games,
            game_factories=game_factories,
            users=users))
        application.add_handlers(r'.*$',
                                 [(r'/lobby/' + str(id(user)),
                                   LobbyWebSocket,
                                   {'user': user})])


class LobbyWebSocket(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        self.user = users[kwargs.pop('user')]
        self.user['lobby_socket'] = self
        print 'Creating a new LobbyWebSocket for %s' % self.user
        super(LobbyWebSocket, self).__init__(*args, **kwargs)

    def on_close(self):
        try:
            del self.user['lobby_socket']
        except KeyError:
            pass

    @classmethod
    def update(self):
        print 'Updating the lobby'
        for user in users.values():
            try:
                if not 'lobby_socket' in user:
                    continue
                user['lobby_socket'].write_message('update')
            except:
                traceback.print_exc()


class NewGameHandler(BaseHandler):

    def get(self):
        LobbyWebSocket.update()
        players = int(self.get_argument('players', 4))
        game_factory = game_factories[
            self.get_argument('game', 'crosspurposes')]
        game = game_factory(players)
        game.url = '/' + str(id(game))
        games.append(game)
        application.add_handlers(r'.*$', [(r'/' + str(
            id(game)), NewPlayerHandler, {'game': game})])
        self.redirect('/' + str(id(game)))


class NewPlayerHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        self.game = kwargs['game']
        super(NewPlayerHandler, self).__init__(*args)

    def get(self):
        player = self.game.player_factory(
            self.get_current_user(), game=self.game)
        self.game.add_player(player, player)
        users[self.get_current_user()]['player'] = player
        users[self.get_current_user()]['game'] = self.game
        for template_name, template_file in self.game.templates.iteritems():
            application.add_handlers(r'.*$',
                                     [(self.request.uri + '/' + str(id(player)) + '/' + template_name,
                                       PlayerInfo,
                                       {'player': player, 'template': template_file})])
        application.add_handlers(r'.*$',
                                 [(self.request.uri + '/' + str(id(player)),
                                   PlayerInfo,
                                   {'player': player, 'template': self.game.player_template})])
        application.add_handlers(r'.*$',
                                 [(self.request.uri + '/' + str(id(player)) + '/get',
                                   PlayerWebSocket,
                                   {'player': player})])
        self.redirect(self.request.uri + '/' + str(id(player)))


class PlayerInfo(BaseHandler):

    def __init__(self, *args, **kwargs):
        self.player = kwargs.pop('player')
        self.template = kwargs.pop('template')
        super(PlayerInfo, self).__init__(*args, **kwargs)

    def get(self):
        self.write(loader.load(self.template).generate(
            player=self.player, values=Values, suits=Suits))


class PlayerWebSocket(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        self.player = kwargs.pop('player')
        print 'Creating a new playersocket for %s' % self.player.name
        self.player.socket = self
        self.player.left = False
        super(PlayerWebSocket, self).__init__(*args, **kwargs)

    def open(self):
        LobbyWebSocket.update()
        print '%s joined' % (self.player.name)

    def on_close(self):
        LobbyWebSocket.update()
        print '%s left - removing them from the game' % (self.player.name)
        self.player.left = True
        if all([player.left for player in self.player.game.players]):
            try:
                games.remove(self.player.game)
            except:
                print 'Tried to remove a player that was NOT in the game'
                pass

    def on_message(self, message):
        print '%s received "%s"' % (self.player.name, message)
        try:
            params = message.split(' ')
            self.player.callbacks[params[0]](message=' '.join(params[1:]))
        except Exception as e:
            self.player.socket.write_message('Uncaught:' + str(e))
            traceback.print_exc()

settings = {
    'static_path': os.path.join(os.path.realpath(__file__ + '/../'), 'static'),
    'cookie_secret': 'QU%9B4\'?E$@(D0Q($5?@()".8B&%UOD1M5Y.IMD',
    'login_url': '/login'}

application = tornado.web.Application(**settings)
application.add_handlers('.*$', [(r'/', LobbyHandler),
                                 (r'/lobby', LobbyWebSocket),
                                 (r'/new', NewGameHandler),
                                 (r'/login', LoginHandler),
                                 (r'/logout', LogoutHandler),
                                 (r'/quit', QuitHandler)])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9999)
    tornado.ioloop.IOLoop.instance().start()
