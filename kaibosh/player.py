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

    def sort_hand(self, trump):
        def sort(a, b):
            if a.suit == trump and a.value == Values['J']:
                return -1
            if b.suit == trump and b.value == Values['J']:
                return 1
            if a.suit == SameColor[trump] and a.value == Values['J']:
                return -1
            if b.suit == SameColor[trump] and b.value == Values['J']:
                return 1
            if a.suit == trump and b.suit != trump:
                return -1
            if a.suit != trump and b.suit == trump:
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
            return 0
        self.hand.sort(sort)
