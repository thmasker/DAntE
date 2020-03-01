import pandas as pd
import pickle
from weekday_prototypes import get_threshold

from progress.bar import Bar


OUT_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/'
CONS_PATH = OUT_PATH + 'consumptions_byday/'
PROTOS_PATH = OUT_PATH + 'prototypesMEAN.zip'


def normalize(x: pd.DataFrame, mean: float, std: float) -> pd.DataFrame:
	return (x - mean) / std

def denormalize(x: pd.DataFrame, mean: float, std:float) -> pd.DataFrame:
	return x * std + mean

def transform(x: pd.DataFrame, y: pd.DataFrame) -> pd.DataFrame:
	nan = y.isna()			# NaN values
	negatives = y.lt(0)		# Negative values

	if not False in nan or not False in negatives:	# If all y values are inavlid, simply return x
		return x

	x_clean = x.dropna()
	x_mean, x_std = x_clean.mean(), x_clean.std()
	x_norm = normalize(x, x_mean, x_std)

	y_clean = y.dropna()
	y_mean, y_std = y_clean.mean(), y_clean.std()
	y_norm = normalize(y, y_mean, y_std)

	y_norm[nan] = x_norm[nan]
	y_norm[negatives] = x_norm[negatives]

	return denormalize(y_norm, y_mean, y_std)


if __name__ == '__main__':
	protos = pd.read_pickle(PROTOS_PATH)
	counters = pickle.load(open(OUT_PATH + 'counter_ids.pickle', 'rb'))

	bar = Bar('Rebuilding data', max=len(counters))
	for counter_id in counters:
		mean_proto = protos[protos['building_id'] == counter_id]
		mean_proto.reset_index(drop=True, inplace=True)

		df = pd.read_pickle(CONS_PATH + 'counter_' + str(counter_id) + '_byDay.zip')

		threshold = get_threshold(df[df['weekday'] == 6])

		for i in range(len(df)):
			weekday = df['weekday'].iloc[i]

			day_of_week = (weekday == 6) or (weekday == 5)	# It is a Sunday or a Saturday
			august = df.index[i].month == 8					# August is an inactive month
			chirstmas = (df.index[i].month == 12 and df.index[i].day >= 23) or (df.index[i].month == 1 and df.index[i].day >= 6)	# Christmas holidays

			inactive = day_of_week or august or chirstmas

			if inactive:
				df.iloc[i, 2:] = transform(mean_proto[(mean_proto['weekday'] == weekday) & (mean_proto['active'] == False)].iloc[0, 3:], df.iloc[i, 2:])
			else:
				df.iloc[i, 2:] = transform(mean_proto[(mean_proto['weekday'] == weekday) & (mean_proto['active'] == True)].iloc[0, 3:], df.iloc[i, 2:])

		df.insert(2, 'active', True)
		for day in df.index:
			mean = df.loc[day, '0':].mean()	# Calculate daily consumptions mean

			if df.loc[day, 'weekday'] == 6:	# It is a Sunday, thus INACTIVE day
				df.loc[day, 'active'] = False
			elif mean > threshold:
				df.loc[day, 'active'] = True
			else:
				df.loc[day, 'active'] = False

		df.to_pickle(OUT_PATH + 'consumptions/counter_' + str(counter_id) + '_byDay.zip')

		bar.next()
	bar.finish()
