import random
import hashlib

class Player(object):
    def __init__(self, name=None):
        self.hand = []
        self.score = 0
        self.name = name or random.choice(['Fred', 'Bob', 'Lucy', 'Chuck', 'Ted'])

    def hash(self):
        return hashlib.sha1(str(id(self))).hexdigest()

    def receive_hand(self, hand):
        self.hand = hand
        for card in hand:
            card.player = self

    def __repr__(self):
        return self.name
