from cardgame import player

class Player(player.Player):
    def bid(self, bid, message=None):
        self.game.bid(self, bid)

    def play_card(self, card, message=None):
        self.game.play_card(self, card)

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
