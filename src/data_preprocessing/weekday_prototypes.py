import pandas as pd
import numpy as np
import pickle


OUT_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/'


def get_prototype(df: pd.DataFrame, mode: str = 'mean') -> pd.DataFrame:
    weekday = df['weekday'].iloc[0]
    active = df['active'].iloc[0]
    consumer_type = df['type'].iloc[0]

    cons = []
    for i in range(24):
        i_consumptions = []
        for j in range(df.shape[0]):
            i_consumptions.append(df['consumptions'].iloc[j][i])    # i_consumptions correspond to the ith hour

        if mode == 'std':
            cons.append(np.nanstd(i_consumptions))
        else:
            cons.append(np.nanmean(i_consumptions))

    return pd.DataFrame({'weekday': weekday, 'active': active, 'type': consumer_type, 'consumptions': [cons]})


if __name__ == '__main__':
    raw_df = pd.read_pickle(OUT_PATH + 'consumptions.zip')

    mean_proto, std_proto = pd.DataFrame(), pd.DataFrame()
    for d in range(0, 7):
        df = raw_df[raw_df['weekday'] == d]
        df['daily'] = df['consumptions'].apply(np.nansum)

        for a in (True, False):
            df_a = df[df['active'] == a]

            for t in df_a['type'].unique():
                df_t = df_a[df_a['type'] == t]

                mean_proto = mean_proto.append(get_prototype(df_t, mode='mean'), ignore_index=True)
                std_proto = std_proto.append(get_prototype(df_t, mode='std'), ignore_index=True)

    mean_proto.to_pickle(OUT_PATH + 'prototypesMEAN.zip', compression='zip'), std_proto.to_pickle(OUT_PATH + 'prototypesSTD.zip', compression='zip')