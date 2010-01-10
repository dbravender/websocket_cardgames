from deck import Values

class Player(object):
    def __init__(self, name, game):
        self.hand = []
        self.score = 0
        self.name = name
        self.game = game
        self.callbacks = {}

    def rename(self, message):
        old_name = self.name
        self.name = message
        self.game.send(u'%s now goes by %s'.encode('utf-8') % (old_name, self.name))

    def forget(self):
        self.callbacks = {}

    def remember(self, callback, *args, **kwargs):
        def doit(message):
            kwargs['message'] = message
            callback(*args, **kwargs)
        cid = str(id(doit))
        self.callbacks[cid] = doit
        return cid

    def receive_hand(self, hand):
        self.hand = hand

    def __repr__(self):
        return self.name.encode('utf-8')
