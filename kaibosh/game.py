from cardgame.deck import KaiboshDeck, Card, Suit, Suits, Value, Values
from collections import defaultdict
from itertools import cycle
from functools import wraps
import traceback
import hashlib
from cardgame.game import Game, GameException, GameProcedureError, message, OutOfTurn

class MustFollowSuit(GameException): pass

SameColor = {
    Suits['Hearts']  : Suits['Diamonds'],
    Suits['Diamonds']: Suits['Hearts'],
    Suits['Clubs']   : Suits['Spades'],
    Suits['Spades']  : Suits['Clubs']}

from player import Player

class KaiboshGame(Game):
    def __init__(self, *args, **kwargs):
        self.name = "Kaibosh"
        self.next_player = None
        self.trump = None
        self.tricks_won = {}
        self.deck = KaiboshDeck()
        self.number_of_players = 4
        self.high_bid = (None, 0)
        self.player_factory = Player
        self.player_template = 'kaibosh/player.html'
        self.hand_template = 'kaibosh/hand.html'
        super(KaiboshGame, self).__init__(*args, **kwargs)

    def deal(self):
        self.deck = KaiboshDeck()
        self.partners = {self.players[0]: self.players[2],
                         self.players[2]: self.players[0],
                         self.players[1]: self.players[3],
                         self.players[3]: self.players[1]}
        for player in self.players:
            hand = self.deck.cards[len(self.deck.cards)-6:]
            hand.sort()
            self.deck.cards = self.deck.cards[:-6]
            player.receive_hand(hand)
        self.trump = None
        self.tricks_played = 0
        self.bids = {}
        self.trick_cards = []
        self.old_trick_cards = []
        self.tricks_won = defaultdict(lambda: 0)
        self.state = 'bid'
        self.next_player = self.dealers.next()
        self.lead_player = self.next_player
        self.high_bid = (None, 0)
        self.send('New hand')
        self.last_trick_cards = []

    @message(int)
    def bid(self, player, bid):
        if bid > 0 and bid <= self.high_bid[1]:
            raise GameProcedureError('Bid too low. Must be above %s' % self.high_bid[1])
        if bid != 0:
            self.high_bid = (player, bid)
        self.response = u'%s bids %s' % (player, bid)
        self.next_player = self.players[(self.players.index(self.next_player) + 1) % len(self.players)]
        if self.next_player == self.lead_player or bid == 12:
            # the bid went all the way around or someone kaiboshed!
            self.state = 'name_trump'
            if bid == 12:
                self.lead_player = self.high_bid[0]
            self.next_player = self.high_bid[0]

    @message(Suit)
    def name_trump(self, player, trump):
        self.trump = trump
        for player in self.players:
            player.sort_hand(trump)
        self.send('%s named %s trump' % (player, trump))
        self.next_player = self.lead_player
        self.start_trick()

    def start_trick(self):
        self.trick_cards = []
        self.state = 'play_card'

    def treated_suit(self, card):
        if card.value == Values['J'] and card.suit == SameColor[self.trump]:
            return self.trump
        else:
            return card.suit

    def following_suit(self, card, player):
        return self.treated_suit(card) == self.led_suit or self.led_suit not in map(self.treated_suit, player.hand)

    @message(Card)
    def play_card(self, player, card):
        if len(self.trick_cards) == 0:
            # The lead card gives us enough info to create the sorter to
            # determine the winning trick
            self.led_suit = self.treated_suit(card)
            self.trick_sorter = self.card_sorter(trump   =self.trump,
                                                 led_suit=self.led_suit)
        else:
            if not self.following_suit(card, player):
                raise MustFollowSuit('Must follow suit!')
        player.hand.remove(card)
        card.player = player
        self.trick_cards.append(card)
        self.response = u'%s played %s'.encode('utf-8') % (player.name, card)
        self.next_player = self.players[(self.players.index(self.next_player) + 1) % len(self.players)]
        if self.high_bid[1] == 12 and self.next_player == self.partners[self.high_bid[0]]:
            self.next_player = self.players[(self.players.index(self.next_player) + 1) % len(self.players)]
        if len(self.trick_cards) >= self.number_of_players or \
           (self.high_bid[1] == 12 and len(self.trick_cards) >= 3):
            self.trick_cards.sort(self.trick_sorter)
            winner = self.trick_cards[0].player
            self.tricks_won[winner] += 1
            self.next_player = winner
            self.response = u'Trick won by %s'.encode('utf-8') % winner
            self.tricks_played += 1
            if self.tricks_played >= 6:
                self.end_hand()
            else:
                self.last_trick_cards = self.trick_cards[:]
                self.start_trick()

    def end_hand(self):
        partners = [(self.players[0], self.players[2]),
                    (self.players[1], self.players[3])]
        for ps in partners:
            score = self.tricks_won[ps[0]] + self.tricks_won[ps[1]]
            if self.high_bid[0] in ps and self.high_bid[1] == 12:
                # taking all 6 tricks on a Kaibosh is 12 points
                if score == 6:
                    score = 12
            if self.high_bid[0] in ps:
                if score < self.high_bid[1]:
                    score = - self.high_bid[1]
                else:
                    ps[0].score += score
                    ps[1].score += score
        self.deal()

    def card_sorter(self, trump, led_suit):
        def sorter(a, b):
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
            if a.suit == led_suit and b.suit != led_suit:
                return -1
            if b.suit == led_suit and a.suit != led_suit:
                return 1
            return 0
        return sorter
