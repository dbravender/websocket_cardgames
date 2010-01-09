import random
import hashlib

class Player(object):
    def __init__(self, name=None, game=None):
        self.hand = []
        self.score = 0
        self.name = name or random.choice(['Fred', 'Bob', 'Lucy', 'Chuck', 'Ted', 'Tadeo'])
        self.game = game
        self.callbacks = {}

    def forget(self):
        self.callbacks = {}

    def remember(self, callback, *args, **kwargs):
        def doit():
            callback(*args, **kwargs)
        cid = str(id(doit))
        self.callbacks[cid] = doit
        return cid

    def bid(self, bid):
        self.game.message(self, bid)

    def play_card(self, card):
        self.game.message(self, card)

    def receive_hand(self, hand):
        self.hand = hand
        for card in hand:
            card.player = self
        def sort(a, b):
            if a.suit > b.suit:
                return -1
            if b.suit > a.suit:
                return 1
            if a.value.value > b.value.value:
                return -1
            return 1
        self.hand.sort(sort)
        if hasattr(self, 'socket'):
            self.socket.write_message('new_hand')

    def sort_hand(self, named_high, named_suit):
        def sort(a, b):
            if a.suit > b.suit:
                return -1
            if a.suit < b.suit:
                return 1
            if a.value.value > named_high.value and b.value.value <= named_high.value:
                return 1
            if b.value.value > named_high.value and a.value.value <= named_high.value:
                return -1
            if a.value.value > b.value.value:
                return -1
            return 1
        self.hand.sort(sort)

    def __repr__(self):
        return self.name.encode('utf-8')
