# -*- coding: utf-8 -*-

from random import shuffle
import wirepointer

class Value(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        wirepointer.remember(self)
    
    def __repr__(self):
        return self.name.encode('utf-8')

Values = {'2' : Value(u'2' , 2),
          '3' : Value(u'3' , 3),
          '4' : Value(u'4' , 4),
          '5' : Value(u'5' , 5),
          '6' : Value(u'6' , 6),
          '7' : Value(u'7' , 7),
          '8' : Value(u'8' , 8),
          '9' : Value(u'9' , 9),
          '10': Value(u'10', 10),
          'J' : Value(u'J' , 11),
          'Q' : Value(u'Q' , 12),
          'K' : Value(u'K' , 13),
          'A' : Value(u'A' , 14)}

class Suit(object):
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        wirepointer.remember(self)

    def __repr__(self):
        return self.symbol.encode('utf-8')

Suits = {'Hearts'  : Suit(u'Hearts'  , u'♥'),
         'Spades'  : Suit(u'Spades'  , u'♠'),
         'Diamonds': Suit(u'Diamonds', u'♦'),
         'Clubs'   : Suit(u'Clubs'   , u'♣')}

class Card(object):
    def __init__(self, value, suit, player=None):
        self.value = value
        self.suit = suit
        self.player = player
        wirepointer.remember(self)

    @classmethod
    def sort(kls, trump, led_suit, highest):
        def sorter(a, b):
            if a.suit == b.suit:
                if a.value.value > highest.value and b.value.value <= highest.value:
                    return 1
                if b.value.value > highest.value and a.value.value <= highest.value:
                    return -1
                if a.value.value > b.value.value:
                    return -1
                else:
                    return 1
            else:
                if a.suit == trump:
                    return -1
                if b.suit == trump:
                    return 1
                if a.suit == led_suit:
                    return -1
                if b.suit == led_suit:
                    return 1
                return 0
        return sorter

    def image(self):
        return u'<img src="/static/cards/%s%s.png"/>'.encode('utf-8') % (self.value.name, self.suit.name)

    def __repr__(self):
        return u'%s%s'.encode('utf-8') % (self.value.name, self.suit.name)

class Deck(object):
    def __init__(self):
        self.cards = []
        for suit in Suits.values():
            for value in Values.values():
                self.cards.append(Card(value, suit))
        shuffle(self.cards)
        wirepointer.remember(self)
