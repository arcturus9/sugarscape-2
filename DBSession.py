from gcouchbase.connection import GConnection
from couchbase.exceptions import *

class DBSession:
    def __init__(self, host, bucket):
        self.host = host
        self.bucket = bucket
        self.cb = GConnection(host=host, bucket=bucket)
    
    def Save(self, obj):
        key = obj.Key()
        result = self.cb.replace(key, obj.Data())

    def Load(self, obj):
        key = obj.Key()
        result = self.cb.get(key, quiet=True)
        return result

    def Delete(self, obj):
        key = obj.Key()
        self.cb.delete(key, quiet=True)

    def Exists(self, key):
        result = self.cb.get(key, quiet=True)
        return result.success

