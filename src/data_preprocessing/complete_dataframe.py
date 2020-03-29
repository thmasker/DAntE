import pandas as pd
import numpy as np
import pymongo as pm
import datetime
import pickle

from dbbroker import DBBroker

from progress.bar import Bar


OUT_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/'

DB_COUNTERRAW = 'CounterRawConsumption'
START_DAY = 5   # Day starts at 5:00 am


# Database connection
def connectDB() -> pm.MongoClient:
    return DBBroker.getInstance()


# Indexing TimeSeries
def firstHour(db: pm.MongoClient, counter_id: int) -> datetime.datetime:
    return list(db[DB_COUNTERRAW].find({'counterinfo_id': counter_id}).sort('timestamp', pm.ASCENDING).limit(1))[0]['timestamp']

def lastHour(db: pm.MongoClient, counter_id: int) -> datetime.datetime:
    return list(db[DB_COUNTERRAW].find({'counterinfo_id': counter_id}).sort('timestamp', pm.DESCENDING).limit(1))[0]['timestamp']

def createIndex(first: datetime.datetime, last: datetime.datetime) -> pd.DatetimeIndex:
    return pd.date_range(start=first, end=last, freq='1H')


# Obtain consumptions from database
def getDataFrame(db: pm.MongoClient, counter_id: int) -> pd.DataFrame:
    cursor = db[DB_COUNTERRAW].find({'counterinfo_id': counter_id})
    df = pd.DataFrame(list(cursor))
    del df['_id']
    del df['counterinfo_id']
    
    df = df.set_index('timestamp')  # Indexing dataframe by timestamp
    
    return df


# Recalculate days dependending on START_DAY
def calcDay(df: pd.DataFrame) -> pd.DataFrame:
    df['day'] = df.apply(lambda x: (x.name - pd.DateOffset(hours=START_DAY)).date(), axis= 1)
    df['day'] = pd.to_datetime(df['day'])
    
    return df


if __name__ == '__main__':
    db = connectDB()
    
    counters = pickle.load(open(OUT_PATH + 'counter_ids.pickle', 'rb'))

    bar = Bar('Collecting data', max=len(counters))
    consumptions = pd.DataFrame()
    for counter_id in counters:
        # Fix hours to have 24h days
        start = firstHour(db, counter_id).replace(hour=5)
        end = lastHour(db, counter_id).replace(hour=4)
        index = createIndex(start, end)

        df = getDataFrame(db, counter_id)
        df = df.reindex(index=index)
        df = calcDay(df)

        n_days = len(df['day']) // 24
        cons_array = np.asarray(df['consumption'])
        cons_array = cons_array.reshape((n_days, 24))   # Reshape each day with its 24 consumptions

        cons = pd.DataFrame({'consumptions': cons_array.tolist()})

        days = df['day'].drop_duplicates().tolist()

        weekdays = []
        for day in days:
            weekdays.append(day.weekday())

        cons = pd.concat([pd.DataFrame({'day': days, 'weekday': weekdays}), cons], axis=1)
        cons = cons.set_index(['day'])
        cons.insert(0, 'building_id', counter_id)

        consumptions = consumptions.append(cons)
        bar.next()

    bar.finish()
    consumptions.to_pickle(OUT_PATH + 'raw_consumptions.zip', compression='zip')