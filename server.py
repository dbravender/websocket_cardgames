import sys
sys.path.append('tornado')
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.template
import hashlib
import random
import re
import os
import crosspurposes.game
import kaibosh.game
from cardgame.deck import Suits, Values
import traceback

loader = tornado.template.Loader(os.path.join(os.path.join(os.path.realpath(__file__) + '/../'), 'templates'))

game_factories = {
    'kaibosh'      : kaibosh.game.KaiboshGame,
    'crosspurposes': crosspurposes.game.CrossPurposesGame
}

games = []

class LobbyHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load('lobby.html').generate(games=games, game_factories=game_factories))

class NewGameHandler(tornado.web.RequestHandler):
    def get(self):
        players = int(self.get_argument('players', 4))
        game_factory = game_factories[self.get_argument('game', 'crosspurposes')]
        game = game_factory(players)
        game.url = '/' + str(id(game))
        games.append(game)
        application.add_handlers(r'.*$', [(r'/' + str(id(game)), NewPlayerHandler, {'game': game})])
        self.redirect('/' + str(id(game)))

class NewPlayerHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.game = kwargs['game']
        super(NewPlayerHandler, self).__init__(*args)

    def get(self):
        player = self.game.player_factory('Player ' + str(len(self.game.players) + 1), game=self.game)
        self.game.add_player(player, player)
        application.add_handlers(r'.*$',
            [(self.request.uri + '/' + str(id(player)),
             PlayerInfo,
             {'player': player, 'template': self.game.player_template})])
        application.add_handlers(r'.*$',
            [(self.request.uri + '/' + str(id(player)) + '/hand',
             PlayerInfo,
             {'player': player, 'template': self.game.hand_template})])
        application.add_handlers(r'.*$',
            [(self.request.uri + '/' + str(id(player)) + '/get',
             PlayerWebSocket,
             {'player': player})])
        self.redirect(self.request.uri + '/' + str(id(player)))

class PlayerInfo(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.player = kwargs.pop('player')
        self.template = kwargs.pop('template')
        super(PlayerInfo, self).__init__(*args, **kwargs)

    def get(self):
        self.write(loader.load(self.template).generate(player=self.player, values=Values, suits=Suits))

class PlayerWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.player = kwargs.pop('player')
        self.player.socket = self
        self.player.left = False
        super(PlayerWebSocket, self).__init__(*args, **kwargs)

    def open(self):
        self.receive_message(self.on_message)

    def on_connection_close(self):
        self.player.left = True
        self.player.name = 'Open'

    def on_message(self, message):
        try:
            params = message.split(' ')
            self.player.callbacks[params[0]](message=' '.join(params[1:]))
        except Exception, e:
            self.player.socket.write_message('Uncaught:' + str(e))
            traceback.print_exc()
        self.receive_message(self.on_message)

settings = {'static_path': os.path.join(os.path.realpath(__file__ + '/../'), 'static')}

application = tornado.web.Application(**settings)
application.add_handlers('.*$', [(r'/', LobbyHandler)])
application.add_handlers('.*$', [(r'/new', NewGameHandler)])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9999)
    tornado.ioloop.IOLoop.instance().start()
