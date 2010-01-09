from deck import Values

class Player(object):
    def __init__(self, name, game):
        self.hand = []
        self.score = 0
        self.name = name
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
        self.game.bid(self, bid)

    def play_card(self, card):
        self.game.play_card(self, card)

    def receive_hand(self, hand):
        self.hand = hand
        self.hand.sort(self.sort_hand(Values['A'], None))
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
