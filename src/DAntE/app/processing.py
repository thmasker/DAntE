import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def get_consumption_type(df, n):
    '''
    Computes consumer type, based on percentiles
    
    args:
        df -> pd.DataFrame
        n -> int

    returns pd.DataFrame
    '''

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


def dropNan(df):
    '''
    Remove rows which contains NaN values on 'consumptions' column

    args:
        df -> pd.DataFrame

    returns pd.DataFrame
    '''

    nan_rows = []
    
    df.reset_index(inplace=True)
    for i in df.index:
        if True in np.isnan(df['consumptions'].loc[i]):
            nan_rows.append(i)
            
    df.drop(index=nan_rows, inplace=True)
    return df.set_index('day')


def read_data(file):
    '''
    Reads input CSV and creates DataFrame

    args:
        file -> str

    returns pd.DataFrame
    '''

    return pd.read_csv(file, index_col='day', converters={'consumptions': lambda x: list(map(float, x.strip('[]').split()))}, na_values='nan', parse_dates=True, infer_datetime_format=True)


def add_weekday(df):
    '''
    Adds new column, assigning each row's weekday, depending on its index

    args:
        df -> pd.DataFrame

    returns pd.DataFrame
    '''

    days = df.index.drop_duplicates().tolist()

    df.insert(1, 'weekday', -1)
    for day in days:
        df.loc[day, 'weekday'] = day.weekday()

    return df


def removeOutliers(df):
    '''
    Removes days below and beyond the interquartile range of daily consumptions

    args:
        df -> pd.DataFrame

    returns pd.DataFrame
    '''

    q3 = np.percentile(df['total_cons'], 75)
    q1 = np.percentile(df['total_cons'], 25)
    iqr = q3 - q1
        
    return df[(df['total_cons'] > (q1 - 1.5 * iqr)) & (df['total_cons'] < (q3 + 1.5 * iqr))]


def clustering(df):
    '''
    Divides days in two types: working and holiday

    args:
        -> pd.DataFrame

    returns pd.DataFrame
    '''

    X = df['total_cons'].values.reshape(-1, 1)
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    km = KMeans(n_clusters=2).fit(X)

    df.insert(2, 'active', True)
    for i in range(df.shape[0]):
        if km.cluster_centers_[0] < km.cluster_centers_[1]:
            if km.labels_[i] == 0:
                df['active'].iloc[i] = False
        else:
            if km.labels_[i] == 1:
                df['active'].iloc[i] = False
    
    return df


def get_consumer_types(df, n_consumers):
    '''
    Obtains each building consumer type

    args:
        df -> pd.DataFrame
        n_consumers -> int

    returns pd.DataFrame
    '''

    buildings_df = pd.DataFrame()
    for counter_id in df['building_id'].unique():
        partial_df = df[df['building_id'] == counter_id]  # Select current building

        actives = partial_df['total_cons'][partial_df['active']]
        inactives = partial_df['total_cons'][partial_df['active'] == False]
        buildings_df = buildings_df.append(pd.DataFrame({'building_id': counter_id, 'active': [True, False], 'mean_cons': [actives.mean(), inactives.mean()]}), ignore_index=True)


    actives = get_consumption_type(buildings_df[buildings_df['active']], n_consumers)
    inactives = get_consumption_type(buildings_df[buildings_df['active'] == False], n_consumers)

    return pd.concat([actives, inactives])


def cleanDataFrame(df):
    '''
    Removes outliers from df and divides data in Active/Inactive

    args:
        df -> pd.DataFrame

    returns pd.DataFrame
    '''

    clean_df = pd.DataFrame()
    for counter_id in df['building_id'].unique():
        raw_df = df[df['building_id'] == counter_id]  # Select current building
        
        raw_df['total_cons'] = raw_df['consumptions'].apply(np.nansum)
        
        raw_df = removeOutliers(raw_df)
        clean_df = clean_df.append(clustering(raw_df))

    return clean_df


def setConsumerType(df, types):
    '''
    Joins each building's day with its corresponding consumer type

    args:
        df -> pd.DataFrame
        types -> pd.DataFrame

    returns pd.DataFrame
    '''

    df = df.merge(types, on=['building_id', 'active'], how='left').set_index(df.index)
    return df[['building_id', 'weekday', 'active', 'type', 'consumptions']]


def get_prototype(df):
    '''
    Obtains prototype for given weekday, active and consumer type consumptions

    args:
        df -> pd.DataFrame

    returns Tuple[pd.DataFrame, pd.DataFrame]
    '''

    weekday = df['weekday'].iloc[0]
    active = df['active'].iloc[0]
    consumer_type = df['type'].iloc[0]

    mean, std = [], []
    for i in range(24):
        i_consumptions = []
        for j in range(df.shape[0]):
            i_consumptions.append(df['consumptions'].iloc[j][i])    # i_consumptions correspond to the ith hour

        std.append(np.nanstd(i_consumptions))
        mean.append(np.nanmean(i_consumptions))

    return pd.DataFrame({'weekday': weekday, 'active': active, 'type': consumer_type, 'consumptions': [mean]}), pd.DataFrame({'weekday': weekday, 'active': active, 'type': consumer_type, 'consumptions': [std]})


def getPrototypes(df):
    '''
    Obtains std and mean prototypes for given df

    args:
        df -> pd.DataFrame

    returns Tuple[pd.DataFrame, pd.DataFrame]
    '''

    mean_proto, std_proto = pd.DataFrame(), pd.DataFrame()
    for d in range(0, 7):
        day_df = df[df['weekday'] == d]

        for a in (True, False):
            activity_df = day_df[day_df['active'] == a]

            for t in activity_df['type'].unique():
                mean, std = get_prototype(activity_df[activity_df['type'] == t])

                mean_proto = mean_proto.append(mean, ignore_index=True)
                std_proto = std_proto.append(std, ignore_index=True)

    return mean_proto, std_proto


def getConsumptions(mean_proto, std_proto, accuracy):
    '''
    Creates a whole day (24 hours of consumptions) randomly selected from a normal distribution with mean mean_proto and standard deviation std_proto * window_size

    args:
        mean_proto -> np.array
        std_proto -> np.array
        window_size -> float

    returns np.array
    '''

    return np.random.normal(mean_proto, np.multiply(std_proto, accuracy))


def generateConsumptions(start, end, consumer_type, active, mean_protos, std_protos, accuracy=0.3):
    '''
    Creates a whole period of consumptions

    args:
        start -> datetime.datetime
        end -> datetime.datetime
        consumer_type -> int
        active -> bool
        window_size -> float
        mean_protos -> pd.DataFrame
        std_protos -> pd.DataFrame

    returns pd.Series
    '''

    days = pd.date_range(start=start, end=end, freq='D')

    mean_proto = mean_protos[(mean_protos['active'] == active) & (mean_protos['type'] == consumer_type)]
    std_proto = std_protos[(std_protos['active'] == active) & (std_protos['type'] == consumer_type)]

    consumptions = []
    for day in days:
        mean = mean_proto[mean_proto['weekday'] == day.weekday()]
        std = std_proto[std_proto['weekday'] == day.weekday()]

        day_consumption = getConsumptions(mean['consumptions'].tolist(), std['consumptions'].tolist(), accuracy)

        for cons in day_consumption:
            for h in cons:
                consumptions.append(h)

    return pd.Series(data=consumptions, index=pd.date_range(start=start, end=end, freq='1H'))


def applySmooth(df, rolling_window, times):
    '''
    Applies a mean rolling window to df

    args:
        df -> pd.Series
        rolling_window -> int
        times -> int

    returns pd.Series
    '''

    for _ in range(times):
        df = df.rolling(rolling_window, min_periods=1).mean()

    return df