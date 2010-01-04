from player import Player
from deck import Deck, Card, Suit
from collections import defaultdict
from itertools import cycle
import hashlib

class IncorrectMessageType(Exception): pass
class GameProcedureError(Exception): pass
class OutOfTurn(Exception): pass

class Bid(object):
    ''' player - player that made the bid
        value - either a Suit or high number, depending on what was called'''
    def __init__(self, player, value):
        self.player = player
        self.value = value

    def __repr__(self):
        return repr(self.value)

class Game(object):
    def __init__(self):
        self.players = []
        self.state = self.players_join
        self.next_player = None

    def hash(self):
        return hashlib.sha1(str(id(self))).hexdigest()

    def players_join(self, player):
        if not isinstance(player, Player):
            raise IncorrectMessageType('Expected a player')
        self.players.append(player)
        if len(self.players) >= 4:
            self.dealers = cycle(self.players)
            self.deal()
    players_join.__name__ = 'joined'

    def deal(self):
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
        self.tricks_won = defaultdict(lambda: 0)
        self.state = self.bid
        self.next_player = self.dealers.next()
        self.lead_player = self.next_player

    def bid(self, bid):
        if not isinstance(bid, Bid):
            raise IncorrectMessageType('Expected a bid')
        if self.bids.get(bid.value, None):
            # Someone else already bid this value
            self.bids[bid.value].append(bid.player)
            if isinstance(bid.value, Suit):
                if self.named_suit:
                    raise GameProcedureError('A suit has already been named')
                self.partners.append(self.bids[bid.value])
                self.named_suit = bid.value
            else:
                if self.named_high:
                    raise GameProcedureError('A high has already been named')
                self.partners.append(self.bids[bid.value])
                self.named_high = bid.value
        else:
            self.bids[bid.value] = [bid.player]
        self.next_player = self.dealers.next()
        if self.named_suit and self.named_high:
            self.next_player = self.lead_player
            self.start_trick()

    def start_trick(self):
        self.trick_cards = []
        self.state = self.play_card

    def play_card(self, card):
        if not isinstance(card, Card):
            raise IncorrectMessageType('Expected a card')
        if len(self.trick_cards) == 0:
            # The lead card gives us enough info to create the sorter to
            # determine the winning trick
            self.trick_sorter = Card.sort(trump   =self.named_suit,
                                          led_suit=card.suit,
                                          highest =self.named_high)
        self.trick_cards.append(card)
        self.next_player = self.players[(self.players.index(self.next_player) + 1) % len(self.players)]
        if len(self.trick_cards) >= 4:
            self.trick_cards.sort(self.trick_sorter)
            winner = self.trick_cards[0].player
            self.tricks_won[winner] += 1
            self.next_player = winner
            self.tricks_played += 1
            if self.tricks_played >= 13:
                self.end_hand()
            else:
                self.start_trick()
    play_card.__name__ = 'played the'

    def end_hand(self):
        for ps in self.partners:
            score = (self.tricks_won[ps[0]] + 1) * (self.tricks_won[ps[1]] + 1)
            ps[0].score += score
            ps[1].score += score
        self.deal()

    def send(self, message):
        print message
        pass

    def message(self, player, message):
        if self.next_player and player != self.next_player:
            raise OutOfTurn()
        self.current_player = player
        self.current_state = self.state
        try:
            response = self.state(message) or ''
            self.send(str(self.current_player) + ' ' + self.current_state.__name__ + ' ' + str(message))
            self.send(str(self.next_player) + "'s turn")
        except Exception, e:
            print e
