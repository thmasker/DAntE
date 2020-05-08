from pymongo import MongoClient

HOST = '161.67.142.141'
PORT = 27017
DB = 'differential_uclm_db'

class DBBroker:
    __instance = None

    @staticmethod 
    def getInstance() -> MongoClient:
        if DBBroker.__instance == None:
            DBBroker()
        return DBBroker.__instance

    def __init__(self, host: str = HOST, port: int = PORT, db: str = DB):
        if DBBroker.__instance != None:
            raise Exception("This class is a singleton")
        else:
            DBBroker.__instance = MongoClient(host, port)[db]