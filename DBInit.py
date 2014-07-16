# encoding : utf-8

import copy
import time
from gcouchbase.connection import GConnection
#from couchbase import Couchbase
from couchbase.exceptions import *
from Config import Config
from Data import GrowthMap, MAP_SIZE
from Terrain import Terrain
from Player import Player

PLAYER_COUNT = 4000

players = [Player('player_%d' % i, None) for i in xrange(PLAYER_COUNT)]
terrain = Terrain()
terrain.size = MAP_SIZE
terrain.growth = copy.deepcopy(GrowthMap)
terrain.sugar = copy.deepcopy(GrowthMap)

for player in players:
    player.sugar = 10
    terrain.born(player)

start = time.clock()
cb = GConnection(host=Config['dbHost'], bucket=Config['dbBucket'])
#cb = Couchbase.connect(host=Config['dbHost'], bucket=Config['dbBucket'])

cb.set('sugarscape', {'playerKeys': ','.join((p.Key() for p in players))})

for player in players:
    cb.set(player.Key(), player.Data())

cb.set(terrain.Key(), terrain.Data())

end = time.clock()
print 'success, elapsed:%s' % (end - start)
