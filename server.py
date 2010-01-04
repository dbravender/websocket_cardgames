import sys
sys.path.append('tornado')
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import hashlib
import random
import re
from crosspurposes.game import Game
from crosspurposes.player import Player

class NewGameHandler(tornado.web.RequestHandler):
    def get(self):
        game = Game()
        application.add_handlers(r'.*$', [(r'/' + game.hash(), NewPlayerHandler, {'game': game})])
        self.redirect('/' + game.hash())

class NewPlayerHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.game = kwargs['game']
        super(NewPlayerHandler, self).__init__(*args)

    def get(self):
        player = Player('Player ' + str(len(self.game.players) + 1))
        self.game.message(player, player)
        application.add_handlers(r'.*$', [(self.request.uri + '/' + player.hash(), PlayerWebSocket, {'player': player})])
        self.redirect(self.request.uri + '/' + player.hash())

class PlayerWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.player = kwargs['player']
        super(PlayerWebSocket, self).__init__(*args)

    def open(self):
        self.receive_message(self.on_message)
        self.clients.append(self)
                         
    def on_message(self, message):
        for client in self.clients:
            try:
                client.write_message(u"You said: " + message)
            except:
                self.clients.remove(client)
        self.receive_message(self.on_message)

application = tornado.web.Application()

clients = []

application.add_handlers('.*$', [(r'/', NewGameHandler)])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9999)
    tornado.ioloop.IOLoop.instance().start()
