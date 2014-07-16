# encoding : utf-8
import logging
import logging.config
import random
import gevent
from gevent.queue import Queue
from gevent.event import Event, AsyncResult
from Config import Config
from Constants import *

class MoveJudge(gevent.Greenlet):
    logger = logging.getLogger('judge')
    def __init__(self, terrain):
        self.inbox = Queue()
        self.terrain = terrain
        gevent.Greenlet.__init__(self)

    def _run(self):
        try:
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
                    self.terrain.reserveMove(winRequest[1], winRequest[0])
                    winRequest[1].nextAction.set(Action.MOVE)
                    for req in requests:
                        req[1].nextAction.set(Action.GATHER)
        except KeyboardInterrupt:
            self.logger.debug('end signal')
            raise SystemExit
        except:
            self.logger.error(sys.exc_info()[0])

