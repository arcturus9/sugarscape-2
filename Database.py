from couchbase import Couchbase, FMT_PICKLE
from couchbase.exceptions import *

class DBSession:
    def __init__(self, host, bucket):
        self.host = host
        self.bucket = bucket
        self.cb = Couchbase.connect(host=host, bucket=bucket)
    
    def Save(self, obj):
        key = obj.GetKey()
        try:
            result = cb.replace(key, player.__dict__)
        except NotFoundError:
            result = cb.add(key, player.__dict__)

    def Load(self, obj):
        key = obj.GetKey()
        result = cb.get(key, quiet=True)
        return result

    def Delete(self, obj):
        key = obj.GetKey()
        cb.delete(key, quiet=True)
