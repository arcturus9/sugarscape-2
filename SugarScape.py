#encoding:utf-8

import random
import time
import sys
from itertools import compress
import gevent
from gevent.queue import Queue
from gevent.event import Event, AsyncResult

MOVE_DIRECTION = [
    (-1, 1) , (0, 1) , (1, 1),
    (-1, 0) ,          (1, 0),
    (-1, -1), (0, -1), (1, -1)
    ]


class Action:
    MOVE = 1
    GATHER = 2


class Player(gevent.Greenlet):
    def __init__(self, terrain, judge):
        self.nextAction = AsyncResult()
        self.tick = Event()
        self.sugar = 0
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
            nextPosition = decideNextAction()
            action = self.nextAction.get()

            if action == Action.MOVE:
                self.move(nextPosition)
            elif action == Action.GATHER:
                self.gather()
            
            self.consume()

        self.terrain.died(self)

    def decideNextAction(self):
        sugarOnCurrentPos = self.terrain.peek(self.position)
        existPlayerAlready = lambda pos: return self.terrain.existPlayer(pos)
        noNeedToMove = lambda pos: sugarOnCurrentPos and self.terrain.peek(pos) =< sugarOnCurrentPos

        x, y = self.position
        candidates = [(x + dx, y + dy) for dx, dy in MOVE_DIRECTION if x + dx >= 0 and y + dy >= 0]

        selectors = (existPlayerAlready(pos) or noNeedToMove(pos) for pos in candidates)
        for i, s in enumerate(compress(candidates, selectors)):
            candidates[i] = s
        del candidates[i + 1:]

        self.judge.inbox.put((random.choice(candidates), self))

    def move(self, position):
        self.terrain.move(self.position, position)

    def gather(self):
        self.sugar += self.terrain.gather(self.position)

    def consume(self):
        if self.sugar <= 0:
            self.running = False
            return

        self.sugar -= self.consumeRate


class MoveJudge(gevent.Greenlet):
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

                winRequest = requests.pop(random.randrange(len(x)))
                self.terrain.reserveMove(winRequest[0])
                winRequest[1].nextAction.set(Action.MOVE)
                for req in requests:
                    req[1].nextAction.set(Action.GATHER)


class Terrain(gevent.Greenlet):
    def __init__(self, size, growthMap):
        self.size = size
        self.growthMap = growthMap[:]
        self.sugarMap = growthMap[:]
        self.players = []
        self.positions = set()
        self.reservedPositions = set()

    def born(self, player):
        if player not in self.players:
            self.players.append(player)
            self.scatter(player)
    
    def died(self, player):
        if player in self.players:
            self.players.remove(player)
            self.positions.remove(player.position)

    def scatter(self, player):
        position = (random.randrange(size), random.randrange(size))
        while self.existPlayer(position):
            position = (random.randrange(size), random.randrange(size))

        self.positions.add(position)
        self.players.append(player)

    def peek(self, position):
        x, y = position
        return self.sugarMap[y][x]

    def existPlayer(self, position):
        return position in self.positions or position in self.reservedPositions

    def reserveMove(self, position):
        self.reservedPositions.add(position)

    def movePlayer(self, oldPosition, newPosition):
        self.reservedPositions.remove(newPosition)
        self.positions.remove(oldPosition)
        self.positions.add(newPosition)

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
                player.tick.set()


