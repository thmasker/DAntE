import pandas as pd
import numpy as np
import pickle

from weekday_prototypes import get_threshold

from progress.bar import Bar


OUT_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/'
PROTOS_PATH = OUT_PATH + 'prototypesMEAN.zip'


def normalize(x: np.array, mean: float, std: float) -> np.array:
    return (x - mean) / std

def denormalize(x: np.array, mean: float, std:float) -> np.array:
    return x * std + mean

def transform(x: np.array, y: np.array) -> np.array:
    y = np.asarray(y)

    nans = np.isnan(y)          # NaN values
    negatives = np.less(y, 0)   # Negative values

    x_mean, x_std = np.mean(x), np.std(x)
    x_norm = normalize(x, x_mean, x_std)

    y_clean = y[~nans]
    y_mean, y_std = np.mean(y_clean), np.std(y_clean)
    y_norm = normalize(y, y_mean, y_std)

    y_norm[nans] = x_norm[nans]
    y_norm[negatives] = x_norm[negatives]

    return denormalize(y_norm, y_mean, y_std)


if __name__ == '__main__':
    protos = pd.read_pickle(PROTOS_PATH)
    counters = pickle.load(open(OUT_PATH + 'counter_ids.pickle', 'rb'))

    raw_df = pd.read_pickle(OUT_PATH + 'raw_consumptions.zip')

    bar = Bar('Rebuilding data', max=len(counters))
    clean_consumptions = pd.DataFrame()
    for counter_id in counters:
        mean_proto = protos[protos['building_id'] == counter_id]
        mean_proto.reset_index(drop=True, inplace=True)

        df = raw_df[raw_df['building_id'] == counter_id]

        threshold = get_threshold(df[df['weekday'] == 6])

        df.insert(2, 'active', True)
        for date in df.index:
            weekday = df.loc[date, 'weekday']

            day_of_week = (weekday == 6) or (weekday == 5)  # It is a Sunday or a Saturday
            august = (date.month == 8)                      # August is an inactive month
            christmas = (date.month == 12 and date.day >= 23) or (date.month == 1 and date.day >= 6)    # Christmas holidays

            inactive = (day_of_week or august or christmas)

            if inactive:
                df['consumptions'].loc[date] = transform(mean_proto['consumptions'][(mean_proto['weekday'] == weekday) & (mean_proto['active'] == False)].iloc[0], df.loc[date, 'consumptions'])
            else:
                df['consumptions'].loc[date] = transform(mean_proto['consumptions'][(mean_proto['weekday'] == weekday) & (mean_proto['active'] == True)].iloc[0], df.loc[date, 'consumptions'])

            mean = np.sum(df.loc[date, 'consumptions']) # Calculate daily consumption

            if df.loc[date, 'weekday'] == 6:	# It is a Sunday, thus INACTIVE day
                df.loc[date, 'active'] = False
            elif mean > threshold:
                df.loc[date, 'active'] = True
            else:
                df.loc[date, 'active'] = False

        clean_consumptions = clean_consumptions.append(df)

        bar.next()
    bar.finish()

    clean_consumptions.to_pickle(OUT_PATH + 'clean_consumptions.zip')