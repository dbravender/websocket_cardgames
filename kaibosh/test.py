# -*- coding: utf-8 -*-
from mock import patch

from .game import KaiboshGame, OutOfTurn, MustFollowSuit
from cardgame.deck import Suits, Values, Card
from .player import Player
import kaibosh.game


class TestKaibosh(object):

    def setUp(self):
        # immediately run paused events while testing
        def runnext(_, n):
            n()

        kaibosh.game.add_timeout = runnext

    def test_sorter(self):
        g = KaiboshGame()
        sorter = g.card_sorter(
            trump=Suits['Diamonds'], led_suit=Suits['Clubs'])
        jack_of_diamonds = Card(Values['J'], Suits['Diamonds'])
        jack_of_hearts = Card(Values['J'], Suits['Hearts'])
        ace_of_clubs = Card(Values['A'], Suits['Clubs'])
        king_of_clubs = Card(Values['K'], Suits['Clubs'])
        ace_of_hearts = Card(Values['A'], Suits['Hearts'])
        assert sorted([jack_of_hearts,
                       ace_of_clubs], sorter)[0] == jack_of_hearts
        assert sorted([jack_of_hearts,
                       jack_of_diamonds], sorter)[0] == jack_of_diamonds
        assert sorted([ace_of_clubs,
                       ace_of_hearts], sorter)[0] == ace_of_clubs
        assert sorted([ace_of_clubs,
                       king_of_clubs], sorter)[0] == ace_of_clubs

    def test_setup(self):
        g = KaiboshGame()
        p1 = Player('Alice', g)
        p2 = Player('Bob', g)
        p3 = Player('Chuck', g)
        p4 = Player(u'댄', g)
        self.players = [p1, p2, p3, p4]
        assert g.state == 'add_player'
        g.add_player(p1, p1)
        g.add_player(p2, p2)
        g.add_player(p3, p3)
        g.add_player(p4, p4)
        assert g.state == 'bid'
        jack_of_hearts = Card(Values['J'], Suits['Hearts'])
        jack_of_diamonds = Card(Values['J'], Suits['Diamonds'])
        queen_of_clubs = Card(Values['Q'], Suits['Clubs'])
        ten_of_spades = Card(Values['10'], Suits['Spades'])
        p1.hand = []
        p2.hand = []
        p3.hand = []
        p4.hand = []
        for _ in xrange(6):
            p1.hand.append(jack_of_hearts)
            p2.hand.append(jack_of_diamonds)
            p3.hand.append(queen_of_clubs)
            p4.hand.append(ten_of_spades)
        self.render_template()
        p1.bid(0)
        p2.bid(1)
        try:
            p3.bid(1)
            assert False, 'Should complain about the bid being too low'
        except:
            assert True
        p3.bid(4)
        p4.bid(0)
        assert g.score == [
            {'bidder': p3, 'bid': 4, 'trump': None, 'made_it': None, 'scores': ['-', '-']}]
        assert g.high_bid == (p3, 4)
        assert g.state == 'name_trump'
        p3.name_trump(Suits['Hearts'])
        assert g.score == [
            {'bidder': p3, 'bid': 4, 'trump': Suits['Hearts'], 'made_it': None, 'scores': ['-', '-']}]
        assert g.state == 'play_card'
        assert g.next_player == p1
        p1.play_card(jack_of_hearts)
        self.render_template()
        try:
            p1.play_card(jack_of_hearts)
            assert False, 'Out of turn not raised'
        except OutOfTurn:
            assert True
        p2.hand.append(queen_of_clubs)
        try:
            p2.play_card(queen_of_clubs)
            assert False, 'Must follow suit should raise'
        except MustFollowSuit:
            assert True
        p2.hand.remove(queen_of_clubs)
        p2.play_card(jack_of_diamonds)
        p3.play_card(queen_of_clubs)
        p4.play_card(ten_of_spades)
        assert g.tricks_won[p1] == 1
        assert g.next_player == p1
        for _ in xrange(5):
            p1.play_card(jack_of_hearts)
            p2.play_card(jack_of_diamonds)
            p3.play_card(queen_of_clubs)
            p4.play_card(ten_of_spades)
            self.render_template()
        assert g.state == 'bid'
        assert p1.score == 6
        assert p2.score == 0
        assert p3.score == 6
        assert p4.score == 0
        p1.hand = []
        p2.hand = []
        p3.hand = []
        p4.hand = []
        for _ in xrange(6):
            p1.hand.append(jack_of_hearts)
            p2.hand.append(queen_of_clubs)
            p3.hand.append(jack_of_diamonds)
            p4.hand.append(ten_of_spades)
        p2.bid(3)
        p3.bid(12)
        assert g.state == 'name_trump'
        assert g.next_player == p3
        p3.name_trump(Suits['Diamonds'])
        for _ in xrange(6):
            p3.play_card(jack_of_diamonds)
            p4.play_card(ten_of_spades)
            p2.play_card(queen_of_clubs)
            self.render_template()
        assert g.score[0] == {'bidder': p3,
                              'bid': 12,
                              'trump': Suits['Diamonds'],
                              'made_it': True,
                              'scores': [18, 0]}

    def render_template(self):
        import os
        import sys
        sys.path.append('tornado')
        from tornado import template
        loader = template.Loader(os.path.join(os.path.join(
            os.path.realpath(__file__) + '/../../'), 'templates'))
        for player in self.players:
            loader.load(player.game.templates['hand']).generate(player=player)
            loader.load(player.game.templates['hand']).generate(player=player)
