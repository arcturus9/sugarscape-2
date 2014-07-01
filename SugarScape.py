#encoding:utf-8

import random
import time
import sys
import gevent
from gevent.queue import Queue
from gevent.event import Event

class Player(gevent.Greenlet):
    def __init__(self, terrain, judge):
        self.nextAction = Event()
        self.sugar = 0
        gevent.Greenlet.__init__(self)

    def _run(self):
        pass

    def decideNextAction(self):
        pass

    def move(self, position):
        pass

    def gather(self):
        pass

    def comsume(self):
        pass

class MoveJudge(gevent.Greenlet):
    def __init__(self):
        self.inbox = Queue()
        gevent.Greenlet.__init__(self)

    def _run(self):
        pass

class Terrain:
    def __init__(self, size, growthMap):
        self.size = size
        self.growthMap = growthMap
        self.positions = set()

    def scatter(self, players):
        pass

    def existPlayer(self, position):
        pass

    def movePlayer(self, oldPosition, newPosition):
        pass
    
    def grow(self):
        pass

