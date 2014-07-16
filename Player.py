# encoding : utf-8
import logging
import logging.config
import random
import sys
import gevent
from gevent.queue import Queue
from gevent.event import Event, AsyncResult
from Config import Config
from Constants import *
from DBDecorator import *


class Player(gevent.Greenlet):
    logger = logging.getLogger('player')
    def __init__(self, key, sugarscape):
        self.nextAction = AsyncResult()
        self.tick = Event()
        self._key = key
        self.sugarscape = sugarscape
        self.consumeRate = Config['consumeRate']
        gevent.Greenlet.__init__(self)

    @SaveObject
    def _run(self):
        try:
            self.running = True
            self.logger.debug('%s start' % self._key)
            while self.running:
                self.tick.wait()
                self.tick.clear()
                nextPosition = self.decideNextAction()
                action = self.nextAction.get()
                self.nextAction = AsyncResult()

                if action == Action.MOVE:
                    self.move(nextPosition)
                elif action == Action.GATHER:
                    self.gather()
                
                self.consume()

        except KeyboardInterrupt:
            self.logger.debug('end signal')
            raise SystemExit
        except:
            self.logger.error('%s,%s,%s' % sys.exc_info())


    @LoadObject
    def load(self):
        self.position = tuple(self.position)

    def born(self, sugar):
        self.sugar = 10
        self.sugarscape.born(self)

    def decideNextAction(self):
        sugarOnHere = self.sugarscape.peek(self.position)
        existPlayerAlready = lambda pos: self.sugarscape.existPlayer(pos)
        noNeedToMove = lambda pos: sugarOnHere and self.sugarscape.peek(pos) <= sugarOnHere

        x, y = self.position
        movable = [(x + dx, y + dy) 
            for dx, dy in MOVE_DIRECTION if self.sugarscape.isMovable((x + dx, y + dy))]

        candidates = []
        for pos in movable:
            if not (existPlayerAlready(pos) or noNeedToMove(pos)):
                candidates.append(pos)

        if not candidates:
            self.nextAction.set(Action.GATHER)
            return (0, 0)

        candidate = random.choice(candidates)
        self.sugarscape.requestMove((candidate, self))
        return candidate

    def move(self, position):
        self.logger.debug('%s moved, previous:%s, current:%s', self._key, self.position, position)
        self.sugarscape.movePlayer(self, position)

    def gather(self):
        self.sugar += self.sugarscape.gather(self.position)

    @SaveObject
    def consume(self):
        if self.sugar <= 0:
            self.dead()
            self.running = False
            return

        self.sugar -= self.consumeRate

    @DeleteObject
    def dead(self):
        self.logger.debug('%s dead, sugar:%d, pos:%s', self._key, self.sugar, self.position)
        self.sugarscape.dead(self)

    def Key(self):
        return self._key

    def Data(self):
        return {
            u'sugar' : self.sugar,
            u'position' : self.position,
        }
