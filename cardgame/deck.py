# -*- coding: utf-8 -*-

from random import shuffle


class Value(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return self.name.encode('utf-8')


Values = {'2': Value(u'2', 2),
          '3': Value(u'3', 3),
          '4': Value(u'4', 4),
          '5': Value(u'5', 5),
          '6': Value(u'6', 6),
          '7': Value(u'7', 7),
          '8': Value(u'8', 8),
          '9': Value(u'9', 9),
          '10': Value(u'10', 10),
          'J': Value(u'J', 11),
          'Q': Value(u'Q', 12),
          'K': Value(u'K', 13),
          'A': Value(u'A', 14)}


class Suit(object):
    def __init__(self, name, symbol, color):
        self.name = name
        self.symbol = symbol
        self.color = color

    def __repr__(self):
        return u'<span style="color:'.encode('utf-8') + self.color.encode('utf-8') + u'">'.encode('utf-8') + self.symbol.encode('utf-8') + u'</span>'.encode('utf-8')


Suits = {'Hearts': Suit(u'Hearts', u'♥', u'red'),
         'Spades': Suit(u'Spades', u'♠', u'black'),
         'Diamonds': Suit(u'Diamonds', u'♦', u'red'),
         'Clubs': Suit(u'Clubs', u'♣', u'black')}


class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def image(self):
        return u'<img border="0" src="/static/cards/%s%s.png"/>'.encode('utf-8') % (self.value.name, self.suit.name)

    def __repr__(self):
        return u'<span style="color:%s">%s%s</span>'.encode('utf-8') % (
            self.suit.color,
            self.value.name,
            self.suit.symbol)


class FullDeck(object):
    def __init__(self):
        self.cards = []
        for suit in Suits.values():
            for value in Values.values():
                self.cards.append(Card(value, suit))
        shuffle(self.cards)


class KaiboshDeck(object):
    def __init__(self):
        self.cards = []
        for suit in Suits.values():
            for value in [Values['9'], Values['10'], Values['J'],
                          Values['Q'], Values['K'], Values['A']]:
                self.cards.append(Card(value, suit))
        shuffle(self.cards)
