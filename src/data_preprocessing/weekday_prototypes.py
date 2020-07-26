import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

from typing import Tuple


OUT_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/'


def getBoxPlot(df: pd.DataFrame) -> plt.Figure:
    df[['h' + str(i) for i in range(24)]] = df.apply(lambda x: x[-1], axis=1, result_type='expand')
    df = df.drop(['building_id', 'weekday', 'active', 'type', 'consumptions'], axis=1)
    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    df.plot(kind='box', figsize=(12,10), ax=ax)
    df.mean().plot(ax=ax, color='red')
    
    return fig


def get_prototype(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
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


if __name__ == '__main__':
    raw_df = pd.read_pickle(OUT_PATH + 'consumptions.zip')

    mean_proto, std_proto = pd.DataFrame(), pd.DataFrame()
    for d in range(0, 7):
        df = raw_df[raw_df['weekday'] == d]

        for a in (True, False):
            df_a = df[df['active'] == a]

            for t in df_a['type'].unique():
                mean, std = get_prototype(df_a[df_a['type'] == t])

                mean_proto = mean_proto.append(mean, ignore_index=True)
                std_proto = std_proto.append(std, ignore_index=True)

    mean_proto.to_pickle(OUT_PATH + 'prototypesMEAN.zip', compression='zip'), std_proto.to_pickle(OUT_PATH + 'prototypesSTD.zip', compression='zip')