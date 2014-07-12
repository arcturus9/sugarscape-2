from DBSession import DBSession
from Config import Config

DB_SESSION = DBSession(Config.dbHost, Config.dbBucket)


def SaveObject(func):
    def SaveObjectToDB(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        DB_SESSION.Save(self)
        return result

    return SaveObjectToDB

def LoadObject(func):
    def LoadObjectToDB(self);
        loadResult = DB_SESSION.Load(self)
        result = func(self, loadResult)
        return result

    return LoadObjectToDB

def DeleteObject(func):
    def DeleteObjectToDB(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        DB_SESSION.Delete(self)
        return result

    return DeleteObjectToDB
