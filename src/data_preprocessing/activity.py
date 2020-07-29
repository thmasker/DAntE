from typing import List

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pickle


OUT_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/'


def get_consumption_type(df: pd.DataFrame, n: int) -> pd.DataFrame:
    increment = 100 / n

    types = []
    for i in range(n):
        if i == n - 1:
            atype = df[df['mean_cons'] >= np.percentile(df['mean_cons'], increment * i)]
        else:
            atype = df[(df['mean_cons'] >= np.percentile(df['mean_cons'], increment * i)) & (df['mean_cons'] < np.percentile(df['mean_cons'], increment * (i + 1)))]

        atype['type'] = i

        types.append(atype)

    return pd.concat(types)


def dropNan(df: pd.DataFrame) -> pd.DataFrame:
    nan_rows = []
    
    for i in df.index:
        if True in np.isnan(df['consumptions'].loc[i]):
            nan_rows.append(i)
            
    return df.drop(index=nan_rows)


if __name__ == '__main__':
    raw = pd.read_csv(OUT_PATH + 'raw_consumptions.csv', index_col='day', converters={'consumptions': lambda x: list(map(float, x.strip('[]').split()))}, na_values='nan', parse_dates=True, infer_datetime_format=True)

    days = raw.index.drop_duplicates().tolist()

    raw.insert(1, 'weekday', -1)
    for day in days:
        raw.loc[day, 'weekday'] = day.weekday()

    raw.reset_index(inplace=True)
    raw = dropNan(raw)
    raw.set_index('day', inplace=True)
    
    clean_df, buildings_df = pd.DataFrame(), pd.DataFrame()
    for counter_id in raw['building_id'].unique():
        raw_df = raw[raw['building_id'] == counter_id]  # Select current building
        
        raw_df['total_cons'] = raw_df['consumptions'].apply(np.nansum)
        
        q3 = np.percentile(raw_df['total_cons'], 75)
        q1 = np.percentile(raw_df['total_cons'], 25)
        iqr = q3 - q1
        
        raw_df = raw_df[(raw_df['total_cons'] > (q1 - 1.5 * iqr)) & (raw_df['total_cons'] < (q3 + 1.5 * iqr))]
        
        X = raw_df['total_cons'].values.reshape(-1, 1)
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        km = KMeans(n_clusters=2).fit(X)

        raw_df.insert(2, 'active', True)
        for i in range(raw_df.shape[0]):
            if km.cluster_centers_[0] < km.cluster_centers_[1]:
                if km.labels_[i] == 0:
                    raw_df['active'].iloc[i] = False
            else:
                if km.labels_[i] == 1:
                    raw_df['active'].iloc[i] = False

        clean_df = clean_df.append(raw_df)

        actives = raw_df['total_cons'][raw_df['active']]
        inactives = raw_df['total_cons'][raw_df['active'] == False]
        buildings_df = buildings_df.append(pd.DataFrame({'building_id': counter_id, 'active': [True, False], 'mean_cons': [actives.mean(), inactives.mean()]}), ignore_index=True)

    actives = get_consumption_type(buildings_df[buildings_df['active']], 3)
    inactives = get_consumption_type(buildings_df[buildings_df['active'] == False], 2)
    types = pd.concat([actives, inactives])

    clean_df = clean_df.merge(types, on=['building_id', 'active'], how='left').set_index(clean_df.index)
    clean_df = clean_df[['building_id', 'weekday', 'active', 'type', 'consumptions']]

    clean_df.to_pickle(OUT_PATH + 'consumptions.zip', compression='zip')