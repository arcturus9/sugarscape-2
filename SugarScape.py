# encoding:utf-8

import random
import time
import sys
import copy
from itertools import compress
import gevent
import logging
import logging.config
from gevent.queue import Queue
from gevent.event import Event, AsyncResult
from Data import GrowthMap

MOVE_DIRECTION = [
    (-1, 1) , (0, 1) , (1, 1),
    (-1, 0) ,          (1, 0),
    (-1, -1), (0, -1), (1, -1)
    ]

logging.config.fileConfig('logging.conf')

class Action:
    MOVE = 1
    GATHER = 2


class Player(gevent.Greenlet):
    logger = logging.getLogger('player')
    def __init__(self, number, terrain, judge):
        self.nextAction = AsyncResult()
        self.tick = Event()
        self.sugar = 10
        self.number = number
        self.terrain = terrain
        self.judge = judge
        self.position = (0, 0)
        self.consumeRate = 1
        gevent.Greenlet.__init__(self)

    def _run(self):
        self.terrain.born(self)
        self.running = True
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

        self.logger.debug('%d player dead', self.number)

        self.terrain.dead(self)

    def decideNextAction(self):
        sugarOnHere = self.terrain.peek(self.position)
        existPlayerAlready = lambda pos: self.terrain.existPlayer(pos)
        noNeedToMove = lambda pos: sugarOnHere and self.terrain.peek(pos) <= sugarOnHere

        x, y = self.position
        movable = [(x + dx, y + dy) 
            for dx, dy in MOVE_DIRECTION if self.terrain.isMovable((x + dx, y + dy))]

        candidates = []
        for pos in movable:
            if not (existPlayerAlready(pos) or noNeedToMove(pos)):
                candidates.append(pos)

        if not candidates:
            self.nextAction.set(Action.GATHER)
            return (0, 0)

        candidate = random.choice(candidates)
        self.judge.inbox.put((candidate, self))
        return candidate

    def move(self, position):
        self.logger.debug('%d player moved, previous:%s, current:%s', self.number, self.position, position)
        self.terrain.movePlayer(self, position)

    def gather(self):
        self.sugar += self.terrain.gather(self.position)

    def consume(self):
        if self.sugar <= 0:
            self.running = False
            return

        self.sugar -= self.consumeRate


class MoveJudge(gevent.Greenlet):
    logger = logging.getLogger('judge')
    def __init__(self, terrain):
        self.inbox = Queue()
        self.terrain = terrain
        gevent.Greenlet.__init__(self)

    def _run(self):
        self.running = True
        
        while self.running:
            moveRequester = []
            while not self.inbox.empty():
                moveRequester.append(self.inbox.get())
            
            if not moveRequester:
                gevent.sleep(0)
                continue

            moveRequester.sort()
            while moveRequester:
                requests = [moveRequester.pop(0)]
                while moveRequester and requests[0][0] == moveRequester[0][0]:
                    requests.append(moveRequester.pop(0))
                if self.terrain.existPlayer(requests[0][0]):
                    for req in requests:
                        req[1].nextAction.set(Action.GATHER)
                    continue

                winRequest = requests.pop(random.randrange(len(requests)))
                self.terrain.reserveMove(winRequest[0])
                winRequest[1].nextAction.set(Action.MOVE)
                for req in requests:
                    req[1].nextAction.set(Action.GATHER)


class Terrain(gevent.Greenlet):
    logger = logging.getLogger('terrain')
    def __init__(self, size, growthMap):
        self.size = size
        self.growthMap = copy.deepcopy(growthMap)
        self.sugarMap = copy.deepcopy(growthMap)
        self.players = []
        self.positions = set()
        self.reservedPositions = set()
        gevent.Greenlet.__init__(self)

    def born(self, player):
        if player not in self.players:
            self.players.append(player)
            self.scatter(player)
    
    def dead(self, player):
        if player in self.players:
            self.players.remove(player)
            self.positions.remove(player.position)

    def scatter(self, player):
        position = (random.randrange(self.size), random.randrange(self.size))
        while self.existPlayer(position):
            position = (random.randrange(self.size), random.randrange(self.size))

        self.positions.add(position)
        self.players.append(player)
        player.position = position

    def peek(self, position):
        x, y = position
        return self.sugarMap[y][x]

    def existPlayer(self, position):
        return position in self.positions or position in self.reservedPositions

    def isMovable(self, position):
        x, y = position
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def reserveMove(self, position):
        self.reservedPositions.add(position)

    def movePlayer(self, player, newPosition):
        self.reservedPositions.remove(newPosition)
        self.positions.remove(player.position)
        self.positions.add(newPosition)
        player.position = newPosition

    def gather(self, position):
        x, y = position
        self.sugarMap[y][x] /= 2
        return self.sugarMap[y][x]
    
    def grow(self):
        for y, line in enumerate(self.growthMap):
            for x, growth in enumerate(line):
                self.sugarMap[y][x] += growth

    def _run(self):
        self.running = True
        while self.running:
            gevent.sleep(0.2)
            self.grow()
            for player in self.players:
                self.logger.debug(player.__dict__)
                player.tick.set()


if __name__ == '__main__':
    terrain = Terrain(len(GrowthMap), GrowthMap)
    judge = MoveJudge(terrain)
    players = [Player(i, terrain, judge) for i in xrange(4000)]

    allObjects = [terrain] + [judge] + players

    for obj in allObjects:
        obj.start()

    gevent.joinall(allObjects)
