# encoding:utf-8
import gevent
import re
from Config import Config
from DBDecorator import *
from Player import Player
from Judge import MoveJudge
from Terrain import Terrain

def itersplit(s, sep=None):
    exp = re.compile(r'\s+' if sep is None else re.escape(sep))
    pos = 0
    while True:
        m = exp.search(s, pos)
        if not m:
            if pos < len(s) or sep is not None:
                yield s[pos:]
            break
        if pos < m.start() or sep is not None:
            yield s[pos:m.start()]
        pos = m.end()


class SugarScape:
    def __init__(self):
        self.players = []
        self.terrain = Terrain()
        self.judge = MoveJudge(self.terrain)

    @LoadObject
    def load(self):
        for key in itersplit(self.playerKeys, ','):
            player = Player(key, self)
            player.load()
            self.players.append(player)

        self.terrain.load(self.players)

    def start(self):
        self.terrain.start()
        self.judge.start()
        for player in self.players:
            player.start()

    @SaveObject
    def join(self):
        try:
            gevent.joinall([self.terrain] + [self.judge] + self.players)
        except SystemExit:
            for player in self.players:
                player.running = False
            gevent.joinall(self.players)
            self.judge.running = False
            self.terrain.running = False
            gevent.joinall([self.terrain])

    @SaveObject
    def born(self, player):
        self.players.append(player)
        return self.terrain.born(player)

    @SaveObject
    def dead(self, player):
        self.players.remove(player)
        return self.terrain.dead(player)
        
    def peek(self, position):
        return self.terrain.peek(position)

    def existPlayer(self, position):
        return self.terrain.existPlayer(position)

    def isMovable(self, position):
        return self.terrain.isMovable(position)

    def requestMove(self, request):
        return self.judge.inbox.put(request)

    def movePlayer(self, player, position):
        return self.terrain.movePlayer(player, position)

    def gather(self, position):
        return self.terrain.gather(position)

    def Data(self):
        return {'playerKeys': ','.join((p.Key() for p in self.players))}

    def Key(self):
        return 'sugarscape'
