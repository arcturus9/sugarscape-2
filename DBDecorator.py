from DBSession import DBSession
from Config import Config

DB_SESSION = DBSession(Config['dbHost'], Config['dbBucket'])

def SaveObject(func):
    def SaveObjectToDB(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        DB_SESSION.Save(self)
        return result

    return SaveObjectToDB

def LoadObject(func):
    def LoadObjectToDB(self, *args, **kwargs):
        loadResult = DB_SESSION.Load(self)
        if loadResult.success:
            for name, value in loadResult.value.iteritems():
                setattr(self, name, value)
        result = func(self, *args, **kwargs)
        return result

    return LoadObjectToDB

def DeleteObject(func):
    def DeleteObjectToDB(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        DB_SESSION.Delete(self)
        return result

    return DeleteObjectToDB
