from itertools import cycle
from player import Player


class GameException(Exception):
    pass


class GameProcedureError(GameException):
    pass


class OutOfTurn(GameException):
    pass


def message(expected_arguments):
    def wrap(method):
        def wrapper(self, player, message):
            try:
                if self.next_player and player != self.next_player:
                    raise OutOfTurn('Out of Turn!')
                if self.state != method.__name__:
                    raise GameProcedureError(
                        'Not currently in the state: %s!' % method.__name__)
                if not isinstance(message, expected_arguments):
                    raise GameProcedureError('Expected different %s but got %s' % (
                        str(type(expected_arguments)), str(type(message))))
                self.response = ''
                method(self, player, message)
                self.send(self.response)
                if self.next_player and self.state != 'wait':
                    self.send(getattr(
                        self, self.state).__name__, self.next_player)
            except GameException, e:
                if hasattr(player, 'socket'):
                    try:
                        player.socket.write_message(str(e))
                    except IOError:
                        print str(e)
                else:
                    raise e
        wrapper.__name__ = method.__name__
        return wrapper
    return wrap


class Game(object):

    def __init__(self, number_of_players=4):
        self.players = []
        self.number_of_players = number_of_players
        self.next_player = None
        self.state = 'add_player'

    @message(Player)
    def add_player(self, _, player):
        self.players.append(player)
        self.response = u'%s joined'.encode('utf-8') % player
        if len(self.players) >= self.number_of_players:
            self.dealers = cycle(self.players)
            self.deal()

    def send(self, message, recipient=None):
        if not recipient:
            for player in self.players:
                if hasattr(player, 'socket') and player.socket:
                    try:
                        player.socket.write_message(message)
                    except IOError, e:
                        print str(e)
        else:
            if hasattr(recipient, 'socket') and recipient.socket:
                try:
                    recipient.socket.write_message(message)
                except IOError:
                    pass
