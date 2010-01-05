from game import Game, Bid
from deck import Suits, Values, Card
from player import Player

def test_setup():
    g = Game()
    p1 = Player('Alice', g)
    p2 = Player('Bob', g)
    p3 = Player('Chuck', g)
    p4 = Player('Dan', g)
    assert g.state == 'players_join'
    g.message(p1, p1)
    g.message(p2, p2)
    g.message(p3, p3)
    g.message(p4, p4)
    print p1.hand[0]
    assert g.state == 'bid'
    g.message(p1, Bid(p1, Suits['Hearts']))
    g.message(p2, Bid(p2, Suits['Hearts']))
    assert g.named_suit == Suits['Hearts']
    g.message(p3, Bid(p3, Values['A']))
    g.message(p4, Bid(p4, Values['A']))
    assert g.named_high == Values['A']
    assert g.state == 'play_card'
    assert g.next_player == p1
    g.message(p1, Card(Values['A'], Suits['Hearts'], p1))
    g.message(p2, Card(Values['K'], Suits['Hearts'], p2))
    g.message(p3, Card(Values['Q'], Suits['Clubs'], p3))
    g.message(p4, Card(Values['10'], Suits['Spades'], p4))
    assert g.tricks_won[p1] == 1
    assert g.next_player == p1
    for i in xrange(12):
        g.message(p1, Card(Values['A'], Suits['Hearts'], p1))
        g.message(p2, Card(Values['K'], Suits['Hearts'], p2))
        g.message(p3, Card(Values['Q'], Suits['Clubs'], p3))
        g.message(p4, Card(Values['10'], Suits['Spades'], p4))
    assert g.state == 'bid'
    assert p1.score == 14
    assert p2.score == 14
    assert p3.score == 1
    assert p4.score == 1
