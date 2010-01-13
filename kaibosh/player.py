from cardgame import player
from cardgame.deck import Values
from kaibosh.game import SameColor

class Player(player.Player):
    def bid(self, bid, message=None):
        self.game.bid(self, bid)

    def play_card(self, card, message=None):
        self.game.play_card(self, card)

    def name_trump(self, suit, message=None):
        self.game.name_trump(self, suit)

    def hand_sorter(self):
        if not self.game.trump:
            return super(Player, self).hand_sorter()
        def sort(a, b):
            if a.suit == self.game.trump and a.value == Values['J']:
                return -1
            if b.suit == self.game.trump and b.value == Values['J']:
                return 1
            if a.suit == SameColor[self.game.trump] and a.value == Values['J']:
                return -1
            if b.suit == SameColor[self.game.trump] and b.value == Values['J']:
                return 1
            if a.suit == self.game.trump and b.suit != self.game.trump:
                return -1
            if a.suit != self.game.trump and b.suit == self.game.trump:
                return 1
            if a.suit == b.suit:
                if a.value > b.value:
                    return -1
                else:
                    return 1
            if a.suit > b.suit:
                return -1
            if a.suit < b.suit:
                return 1
        return sort
