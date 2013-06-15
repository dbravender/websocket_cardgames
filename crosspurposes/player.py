from cardgame import player


class Player(player.Player):

    def bid(self, bid, message=None):
        self.game.bid(self, bid)

    def play_card(self, card, message=None):
        self.game.play_card(self, card)

    def hand_sorter(self):
        def sort(a, b):
            if self.game.named_suit:
                if a.suit != b.suit:
                    if a.suit == self.game.named_suit:
                        return -1
                    if b.suit == self.game.named_suit:
                        return 1
            if a.suit > b.suit:
                return -1
            if a.suit < b.suit:
                return 1
            if self.game.named_high:
                if a.value.value > self.game.named_high.value and b.value.value <= self.game.named_high.value:
                    return 1
                if b.value.value > self.game.named_high.value and a.value.value <= self.game.named_high.value:
                    return -1
                if a.value.value > b.value.value:
                    return -1
                return 1
            else:
                if a.value.value > b.value.value:
                    return -1
                if b.value.value > a.value.value:
                    return 1
                return 0
        return sort
