# encoding:utf-8
import random

MAX_GROWTH = 2
MAP_SIZE = 100

GrowthMap = [[random.randrange(MAX_GROWTH) for i in xrange(MAP_SIZE)] for j in xrange(MAP_SIZE)]

if __name__ == '__main__':
    print GrowthMap
