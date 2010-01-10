from player import Player
from cardgame.deck import FullDeck, Card, Suit, Value
from collections import defaultdict
from itertools import cycle
from functools import wraps
import hashlib
from cardgame.game import Game, GameException, message, OutOfTurn, GameProcedureError

class MustFollowSuit(GameException): pass

class CrossPurposesGame(Game):
    def __init__(self, *args, **kwargs):
        self.name = "Cross Purposes"
        self.next_player = None
        self.named_high = None
        self.named_suit = None
        self.partners = []
        self.tricks_won = {}
        self.deck = FullDeck()
        self.previous_round = {}
        self.player_factory = Player
        self.player_template = 'crosspurposes/player.html'
        self.hand_template = 'crosspurposes/hand.html'
        super(CrossPurposesGame, self).__init__(*args, **kwargs)

    def deal(self):
        if self.number_of_players == 2:
            if not len(self.deck.cards):
                self.deck = FullDeck()
        else:
            self.deck = FullDeck()
        for player in self.players:
            hand = self.deck.cards[len(self.deck.cards)-13:]
            hand.sort()
            self.deck.cards = self.deck.cards[:-13]
            player.receive_hand(hand)
        self.named_suit = None
        self.named_high = None
        self.tricks_played = 0
        self.bids = {}
        self.partners = []
        self.trick_cards = []
        self.last_trick_cards = []
        self.tricks_won = defaultdict(lambda: 0)
        self.state = 'bid'
        self.next_player = self.dealers.next()
        self.lead_player = self.next_player
        self.send('New hand')

    def get_bid(self, bid):
        if isinstance(bid, Suit):
            return self.named_suit
        else:
            return self.named_high

    def set_bid(self, bid):
        if isinstance(bid, Suit):
            self.named_suit = bid
        else:
            self.named_high = bid

    @message((Value, Suit))
    def bid(self, player, bid):
        if self.number_of_players == 2 or self.bids.get(bid, None):
            # Someone else already bid this value
            if self.get_bid(bid):
                raise GameProcedureError('%s has already been named'.encode('utf-8') % self.get_bid(bid))
            if self.number_of_players == 2:
                named = bid
                self.set_bid(bid)
                self.response = u'%s names %s'.encode('utf-8') % (player, bid)
            else:
                self.bids[bid].append(player)
                self.partners.append(self.bids[bid])
                self.set_bid(bid)
                self.response = u'%s and %s name %s'.encode('utf-8') % \
                                                      (self.bids[bid][0],
                                                       self.bids[bid][1],
                                                       bid)
        else:
            self.bids[bid] = [player]
            self.response = u'%s bids %s'.encode('utf-8') % (player, bid)
        self.next_player = self.dealers.next()
        if len(self.partners):
            # Bid goes to the next player who hasn't found a partner yet
            while self.next_player in self.partners[0]:
                self.next_player = self.dealers.next()
        if self.named_suit and self.named_high:
            for player in self.players:
                player.sort_hand(self.named_high, self.named_suit)
            self.next_player = self.lead_player
            self.start_trick()

    def start_trick(self):
        self.trick_cards = []
        self.state = 'play_card'

    @message(Card)
    def play_card(self, player, card):
        if len(self.trick_cards) == 0:
            # The lead card gives us enough info to create the sorter to
            # determine the winning trick
            self.trick_sorter = Card.sort(trump   =self.named_suit,
                                          led_suit=card.suit,
                                          highest =self.named_high)
            self.led_suit = card.suit
        else:
            if card.suit != self.led_suit and self.led_suit in (x.suit for x in player.hand):
                raise MustFollowSuit('Must follow suit!')
        player.hand.remove(card)
        card.player = player
        self.trick_cards.append(card)
        self.response = u'%s played %s'.encode('utf-8') % (player.name, card)
        self.next_player = self.players[(self.players.index(self.next_player) + 1) % len(self.players)]
        if len(self.trick_cards) >= self.number_of_players:
            self.trick_cards.sort(self.trick_sorter)
            winner = self.trick_cards[0].player
            self.tricks_won[winner] += 1
            self.next_player = winner
            self.response = u'Trick won by %s'.encode('utf-8') % winner
            self.tricks_played += 1
            if self.tricks_played >= 13:
                self.end_hand()
            else:
                self.last_trick_cards = self.trick_cards[:]
                self.start_trick()

    def end_hand(self):
        if self.number_of_players == 2:
            if len(self.previous_round):
                for player in self.players:
                    player.score += self.previous_round[player] * self.tricks_won[player]
                self.previous_round = {}
            else:
                for player in self.players:
                    self.previous_round[player] = self.tricks_won[player] + 1
        else:
            for ps in self.partners:
                score = (self.tricks_won[ps[0]] + 1) * (self.tricks_won[ps[1]] + 1)
                ps[0].score += score
                ps[1].score += score
        self.deal()
