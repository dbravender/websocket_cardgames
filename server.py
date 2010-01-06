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
from crosspurposes.game import Game, Message, Bid
from crosspurposes.player import Player
from crosspurposes.deck import Suits, Values, Card
from crosspurposes import wirepointer

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
        self.game.message(player, player)
        application.add_handlers(r'.*$', [(self.request.uri + '/' + str(id(player)), PlayerHome, {'player': player})])
        application.add_handlers(r'.*$', [(self.request.uri + '/' + str(id(player)) + '/get', PlayerWebSocket, {'player': player})])
        application.add_handlers(r'.*$', [(self.request.uri + '/' + str(id(player)) + '/hand', PlayerHand, {'player': player})])
        self.redirect(self.request.uri + '/' + str(id(player)))

class PlayerHome(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.player = kwargs['player']
        super(PlayerHome, self).__init__(*args)

    def get(self):
        self.write(loader.load('player.html').generate(player=self.player, values=Values, suits=Suits))

class PlayerHand(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.player = kwargs['player']
        super(PlayerHand, self).__init__(*args)

    def get(self):
        self.write(loader.load('hand.html').generate(player=self.player, values=Values, suits=Suits))

class PlayerWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.player = kwargs['player']
        self.player.socket = self
        super(PlayerWebSocket, self).__init__(*args)

    def open(self):
        self.receive_message(self.on_message)
    
    def on_message(self, message):
        command, params = message.split(' ')[0], ' '.join(message.split(' ')[1:])
        if command == 'bid':
            bid = Bid(self.player, wirepointer.get_object(params))
            self.player.game.message(self.player, bid)
        if command == 'play':
            card = wirepointer.get_object(params)
            self.player.game.message(self.player, card)
        if command == 'name':
            old_name = self.player.name
            self.player.name = params
            self.player.game.send(u'%s now goes by %s'.encode('utf-8') % (old_name, self.player.name))
        self.receive_message(self.on_message)

settings = {'static_path': os.path.join(os.path.realpath(__file__ + '/../'), 'static')}

application = tornado.web.Application(**settings)
application.add_handlers('.*$', [(r'/', NewGameHandler)])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9999)
    tornado.ioloop.IOLoop.instance().start()
