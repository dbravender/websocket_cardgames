from player import Player
from deck import Deck, Card, Suit, Value
from collections import defaultdict
from itertools import cycle
import hashlib

class GameException(Exception): pass
class IncorrectMessageType(GameException): pass
class GameProcedureError(GameException): pass
class OutOfTurn(GameException): pass
class MustFollowSuit(GameException): pass

class Game(object):
    def __init__(self, number_of_players=4):
        self.players = []
        self.number_of_players = number_of_players
        self.state = 'players_join'
        self.next_player = None
        self.named_high = None
        self.named_suit = None
        self.partners = []
        self.tricks_won = {}
        self.deck = Deck()
        self.previous_round = {}

    def players_join(self, _, player):
        if not isinstance(player, Player):
            raise IncorrectMessageType('Expected a player')
        self.players.append(player)
        self.response = u'%s joined'.encode('utf-8') % player
        if len(self.players) >= self.number_of_players:
            self.dealers = cycle(self.players)
            self.deal()

    def deal(self):
        if self.number_of_players == 2:
            if not len(self.deck.cards):
                self.deck = Deck()
        else:
            self.deck = Deck()
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
        self.old_trick_cards = []
        self.tricks_won = defaultdict(lambda: 0)
        self.state = 'bid'
        self.next_player = self.dealers.next()
        self.lead_player = self.next_player
        self.send('New hand')

    def bid(self, player, bid):
        if not (isinstance(bid, Suit) or isinstance(bid, Value)):
            raise IncorrectMessageType('Expected a bid')
        if self.number_of_players == 2 or self.bids.get(bid, None):
            # Someone else already bid this value
            if isinstance(bid, Suit):
                if self.named_suit:
                    raise GameProcedureError('A suit has already been named')
                if self.number_of_players == 2:
                    self.named_suit = bid
                    self.response = u'%s names %s'.encode('utf-8') % (player, bid)
                else:
                    self.bids[bid].append(player)
                    self.partners.append(self.bids[bid])
                    self.named_suit = bid
                    self.response = u'%s and %s name %s'.encode('utf-8') % \
                                                          (self.bids[bid][0],
                                                           self.bids[bid][1],
                                                           self.named_suit)
            else:
                if self.named_high:
                    raise GameProcedureError('A high has already been named')
                if self.number_of_players == 2:
                    self.named_high = bid
                    self.response = u'%s names %s'.encode('utf-8') % (player, bid)
                else:
                    self.bids[bid].append(player)
                    self.partners.append(self.bids[bid])
                    self.named_high = bid
                    self.response = u'%s and %s name %s'.encode('utf-8') % \
                                                          (self.bids[bid][0],
                                                           self.bids[bid][1],
                                                           self.named_high)
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

    def play_card(self, player, card):
        if not isinstance(card, Card):
            raise IncorrectMessageType('Expected a card')
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

    def send(self, message, recipient=None):
        if not recipient:
            for player in self.players:
                if hasattr(player, 'socket'):
                    player.socket.write_message(message)
        else:
            if hasattr(recipient, 'socket'):
                recipient.socket.write_message(message)

    def message(self, player, message):
        try:
            if self.next_player and player != self.next_player:
                raise OutOfTurn('Out of Turn!')
            self.current_state = getattr(self, self.state)
            self.response = ''
            getattr(self, self.state)(player, message)
            self.send(self.response)
            if self.next_player:
                self.send(getattr(self, self.state).__name__, self.next_player)
        except GameException, e:
            if hasattr(player, 'socket'):
                player.socket.write_message(str(e))
            else:
                print str(e)
