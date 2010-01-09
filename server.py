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
from crosspurposes.game import Game
from crosspurposes.player import Player
from crosspurposes.deck import Suits, Values

loader = tornado.template.Loader(os.path.join(os.path.join(os.path.realpath(__file__) + '/../'), 'templates'))

class NewGameHandler(tornado.web.RequestHandler):
    def get(self):
        players = int(self.get_argument('players', 4))
        game = Game(players)
        application.add_handlers(r'.*$', [(r'/' + str(id(game)), NewPlayerHandler, {'game': game})])
        self.redirect('/' + str(id(game)))

class NewPlayerHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.game = kwargs['game']
        super(NewPlayerHandler, self).__init__(*args)

    def get(self):
        player = Player('Player ' + str(len(self.game.players) + 1), game=self.game)
        self.game.add_player(player, player)
        application.add_handlers(r'.*$',
            [(self.request.uri + '/' + str(id(player)),
             PlayerInfo,
             {'player': player, 'template': 'player.html'})])
        application.add_handlers(r'.*$',
            [(self.request.uri + '/' + str(id(player)) + '/hand',
             PlayerInfo,
             {'player': player, 'template': 'hand.html'})])
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
        super(PlayerWebSocket, self).__init__(*args, **kwargs)

    def open(self):
        self.receive_message(self.on_message)
    
    def on_message(self, message):
        try:
            self.player.callbacks[message]()
        except Exception, e:
            self.player.socket.write_message('Uncaught:' + str(e))
        self.receive_message(self.on_message)

settings = {'static_path': os.path.join(os.path.realpath(__file__ + '/../'), 'static')}

application = tornado.web.Application(**settings)
application.add_handlers('.*$', [(r'/', NewGameHandler)])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9999)
    tornado.ioloop.IOLoop.instance().start()
