# encoding : utf-8
import copy
import random
import logging
import logging.config
import gevent
from gevent.queue import Queue
from gevent.event import Event, AsyncResult
from Config import Config
from Constants import *
from DBDecorator import *

class Terrain(gevent.Greenlet):
    logger = logging.getLogger('terrain')
    def __init__(self):
        self.players = []
        self.positions = {}
        self.reservedPositions = {}
        gevent.Greenlet.__init__(self)

    @LoadObject
    def load(self, players):
        for player in players:
            pos = tuple(self.playerSave[player.Key()])
            self.positions[pos] = player
        self.players.extend(players)
        for player, pos in self.reservePositionSave.iteritems():
            self.reservedPositions[pos] = player
        self.logger.debug('player loaded')
        
    def born(self, player):
        if player not in self.players:
            self.players.append(player)
            self.scatter(player)
    
    def dead(self, player):
        if player in self.players:
            self.players.remove(player)
            self.positions.pop(player.position)

    def scatter(self, player):
        position = (random.randrange(self.size), random.randrange(self.size))
        while self.existPlayer(position):
            position = (random.randrange(self.size), random.randrange(self.size))

        self.positions[position] = player
        self.players.append(player)
        player.position = position

    def peek(self, position):
        x, y = position
        return self.sugar[y][x]

    def existPlayer(self, position):
        return position in self.positions or position in self.reservedPositions

    def isMovable(self, position):
        x, y = position
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def reserveMove(self, player, position):
        self.reservedPositions[position] = player

    def movePlayer(self, player, newPosition):
        if newPosition not in self.reservedPositions:
            logger.error(u'invalid move position')
            return
        if self.reservedPositions[newPosition] != player:
            logger.error(u'reserved position for another player')
        self.reservedPositions.pop(newPosition)
        self.positions.pop(player.position)
        self.positions[newPosition] = player
        player.position = newPosition

    def gather(self, position):
        x, y = position
        self.sugar[y][x] /= 2
        return self.sugar[y][x]
    
    @SaveObject
    def grow(self):
        for y, line in enumerate(self.growth):
            for x, growth in enumerate(line):
                self.sugar[y][x] += growth

    def _run(self):
        self.running = True
        while self.running:
            gevent.sleep(0.2)
            self.grow()
            for player in self.players:
                self.logger.debug('%s: %d, %s' % (player.Key(), player.sugar, player.position))
                player.tick.set()

    def Key(self):
        return 'terrain'

    def Data(self):
        playerSave = {}
        for pos, player in self.positions.iteritems():
            playerSave[player.Key()] = pos
        
        reservePositionSave = {}
        for pos, player in self.reservedPositions.iteritems():
            reservePositionSave[player.Key()] = pos

        return {
            'size': self.size,
            'growth': self.growth,
            'sugar': self.sugar,
            'playerSave': playerSave,
            'reservePositionSave': reservePositionSave,
        }

