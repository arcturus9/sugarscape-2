import sys
import logging
from gcouchbase.connection import GConnection
from couchbase.exceptions import *
from Config import Config


class DBSession:
    logger = logging.getLogger('dbsession')
    def __init__(self, host, bucket):
        self.host = host
        self.bucket = bucket
        self.cb = GConnection(host=host, bucket=bucket)

    def Save(self, obj):
        try:
            key = obj.Key()
            result = self.cb.replace(key, obj.Data())
        except Exception, e:
            self.logger.error('%s,%s,%s' % sys.exc_info())

    def Load(self, obj):
        try:
            key = obj.Key()
            result = self.cb.get(key, quiet=True)
            return result
        except Exception, e:
            self.logger.error('%s,%s,%s' % sys.exc_info())

    def Delete(self, obj):
        try:
            key = obj.Key()
            self.cb.delete(key, quiet=True)
        except Exception, e:
            self.logger.error('%s,%s,%s' % sys.exc_info())

    def Exists(self, key):
        try:
            result = self.cb.get(key, quiet=True)
            return result.success
        except Exception, e:
            self.logger.error('%s,%s,%s' % sys.exc_info())

