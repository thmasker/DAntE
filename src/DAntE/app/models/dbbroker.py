import pandas as pd

from app import mongo


def parseData(data):
    df = pd.DataFrame()
    for e in data:
        new = pd.DataFrame(e['data'])
        df = df.append(new, ignore_index=True)

    return df

def insertRawData(collection, owner_id, project, df):
    df.reset_index(inplace=True)

    data = []
    for building_id in df['building_id'].unique():
        current = df[df['building_id'] == building_id]
        data.append({'owner_id': owner_id, 'project': project, 'building_id': int(building_id), 'data': current.to_dict('records')})

    return insert_many(collection, data)


def findRawData(collection, project, owner_id):
    data = list(find(collection, {'project': project, 'owner_id': owner_id}))

    df = parseData(data)    
    df.set_index('day', inplace=True)
    return df


def findPrototypes(collection, owner_id):
    data = list(find(collection, {'owner_id': owner_id}))

    df = parseData(data)
    return df


def replace(collection, filter, data):
    return mongo.db[collection].replace_one(filter, data, upsert=True)


def insert_one(collection, data):
    return mongo.db[collection].insert_one(data)


def find_one(collection, data):
    return mongo.db[collection].find_one(data)


def find(collection, data):
    return mongo.db[collection].find(data)


def insert_many(collection, data):
    return mongo.db[collection].insert_many(data)


def distinct(collection, dist, data):
    return mongo.db[collection].distinct(dist, data)