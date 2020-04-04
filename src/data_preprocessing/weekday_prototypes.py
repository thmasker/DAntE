import pandas as pd
import numpy as np
import pickle

from progress.bar import Bar


OUT_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/'


def dropNan(df: pd.DataFrame) -> pd.DataFrame:
    nan_rows = []

    for i in range(df.shape[0]):
        consumptions = df['consumptions'].iloc[i]

        if True in np.isnan(consumptions):
            nan_rows.append(df.index[i])

    return df.drop(index=nan_rows)


def get_threshold(df: pd.DataFrame) -> float:
    df['daily'] = df['consumptions'].apply(np.sum)

    return df['daily'].mean() + df['daily'].std()


def get_prototype(df: pd.DataFrame, counter_id: int, weekday: int, active: bool, type: str = 'mean') -> pd.DataFrame:
    cons = []

    for i in range(24):
        i_consumptions = []
        for j in range(df.shape[0]):
            i_consumptions.append(df['consumptions'].iloc[j][i])    # i_consumptions correspond to the ith hour

        if type == 'std':
            cons.append(np.std(i_consumptions))
        else:
            cons.append(np.mean(i_consumptions))

    return pd.DataFrame({'building_id': counter_id, 'weekday': weekday, 'active': active, 'consumptions': [cons]})


if __name__ == '__main__':
    counters = pickle.load(open(OUT_PATH + 'counter_ids.pickle', 'rb'))

    raw = pd.read_pickle(OUT_PATH + 'raw_consumptions.zip')

    bar = Bar('Collecting data', max=len(counters))
    mean_proto, std_proto = pd.DataFrame(), pd.DataFrame()
    for counter_id in counters:
        raw_df = raw[raw['building_id'] == counter_id]  # Select current building
        
        clean_df = dropNan(raw_df)
        sundays = clean_df[clean_df['weekday'] == 6]    # Select Sundays
        threshold = get_threshold(sundays)

        mean_proto = mean_proto.append(get_prototype(sundays, counter_id, 6, False, type='mean'))
        std_proto = std_proto.append(get_prototype(sundays, counter_id, 6, False, type='std'))
        for i in range(0, 6):
            # i = 5
            df = clean_df[clean_df['weekday'] == i]
            df['daily'] = df['consumptions'].apply(np.sum)   # Get daily consumptions
            
            df_a = df.loc[df['daily'] > threshold]   # Select active days
            mean_proto = mean_proto.append(get_prototype(df_a, counter_id, i, True, type='mean'))
            std_proto = std_proto.append(get_prototype(df_a, counter_id, i, True, type='std'))
            
            df_i = df.loc[df['daily'] <= threshold]  # Select inactive days
            mean_proto = mean_proto.append(get_prototype(df_i, counter_id, i, False, type='mean'))
            std_proto = std_proto.append(get_prototype(df_i, counter_id, i, False, type='std'))

        bar.next()
    bar.finish()

    mean_proto.reset_index(drop=True, inplace=True), std_proto.reset_index(drop=True, inplace=True)
    mean_proto.to_pickle(OUT_PATH + 'prototypesMEAN.zip', compression='zip'), std_proto.to_pickle(OUT_PATH + 'prototypesSTD.zip', compression='zip')