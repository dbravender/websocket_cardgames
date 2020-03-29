class Player(object):

    def __init__(self, name, game):
        self.hand = []
        self.score = 0
        self.name = name
        self.game = game
        self.callbacks = {}
        self.left = False

    def rename(self, message):
        old_name = self.name
        self.name = message
        self.game.send(u'%s now goes by %s'.encode('utf-8') %
                       (old_name, self.name))

    def remember(self, callback, *args):
        def doit(message):
            kwargs = {'message': message}
            callback(*args, **kwargs)
        cid = str(id(doit))
        previous_callback = self.callbacks.get((callback, tuple(args)), None)
        if previous_callback:
            del self.callbacks[str(id(previous_callback))]
        self.callbacks[cid] = doit
        self.callbacks[(callback, tuple(args))] = doit
        return cid

    def receive_hand(self, hand):
        self.hand = hand
        self.sort_hand()

    def sort_hand(self):
        self.hand.sort(self.hand_sorter())

    def hand_sorter(self):
        def compare(a, b):
            if a.suit == b.suit:
                if a.value > b.value:
                    return -1
                else:
                    return 1
            if a.suit > b.suit:
                return -1
            return 1
        return compare

    def __repr__(self):
        return self.name.encode('utf-8')
