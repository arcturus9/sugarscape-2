from couchbase import Couchbase
from couchbase.exceptions import *

class DBSession:
    def __init__(self, host, bucket):
        self.host = host
        self.bucket = bucket
        self.cb = Couchbase.connect(host=host, bucket=bucket)
    
    def Save(self, obj):
        key = obj.Key()
        try:
            result = self.cb.replace(key, obj.Data())
        except NotFoundError:
            result = self.cb.add(key, obj.Data())

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
