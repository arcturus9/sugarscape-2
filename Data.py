# encoding:utf-8
import random

MAX_GROWTH = 2
MAP_SIZE = 150

ProbablityTable = [0 for i in xrange(65)] + [1 for i in xrange(22)] + [2 for i in xrange(13)]
GrowthMap = [[random.choice(ProbablityTable) for i in xrange(MAP_SIZE)] for j in xrange(MAP_SIZE)]

if __name__ == '__main__':
    from collections import Counter
    counter = Counter([])
    for line in GrowthMap:
        counter += Counter(line)

    print counter

