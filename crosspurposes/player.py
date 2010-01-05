import random
import hashlib
import wirepointer

class Player(object):
    def __init__(self, name=None, game=None):
        self.hand = []
        self.score = 0
        self.name = name or random.choice(['Fred', 'Bob', 'Lucy', 'Chuck', 'Ted', 'Tadeo'])
        self.game = game
        wirepointer.remember(self)

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
