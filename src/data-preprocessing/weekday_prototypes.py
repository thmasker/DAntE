import pandas as pd
import pickle

from progress.bar import Bar


CONS_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/consumptions_byday/'
OUT_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/'


def get_threshold(df: pd.DataFrame) -> float:
    df.loc[:, 'mean'] = df.loc[:, '0':].mean(axis=1)	# Calculate daily consumption mean
    mean, std = df['mean'].mean(), df['mean'].std()
    
    return mean + 2 * std	# Calculate threshold based on sundays


def get_prototype(df: pd.DataFrame, counter_id: int, weekday: int, active: bool, type: str = 'mean') -> pd.DataFrame:
	if type == 'std':
		proto = df.loc[:, '0':].std(axis=0)		# Calculate hour consumption std
	else:
		proto = df.loc[:, '0':].mean(axis=0)	# Calculate hour consumption mean

	proto = pd.DataFrame(proto).T	# Force it to be a row
	proto.insert(0, 'active', active)
	proto.insert(0, 'weekday', weekday)
	proto.insert(0, 'building_id', counter_id)

	del proto['mean']

	return proto


if __name__ == '__main__':
	counters = pickle.load(open(OUT_PATH + 'counter_ids.pickle', 'rb'))
	
	bar = Bar('Collecting data', max=len(counters))
	mean_proto, std_proto = pd.DataFrame(), pd.DataFrame()
	for counter_id in counters:
		raw_df = pd.read_pickle(CONS_PATH + 'counter_' + str(counter_id) + '_byDay.zip')
		
		clean_df = raw_df.dropna()
		sundays = clean_df[clean_df['weekday'] == 6]	# Select Sundays
		threshold = get_threshold(sundays)

		mean_proto = mean_proto.append(get_prototype(sundays, counter_id, 6, False, type='mean'))
		std_proto = std_proto.append(get_prototype(sundays, counter_id, 6, False, type='std'))
		for i in range(0, 6):
			df = clean_df[clean_df['weekday'] == i]
			df.loc[:, 'mean'] = df.loc[:, '0':].mean(axis=1)	# Calculate daily consumption mean
			
			df_a = df.loc[df['mean'] >= threshold]	# Select active days
			mean_proto = mean_proto.append(get_prototype(df_a, counter_id, 6, True, type='mean'))
			std_proto = std_proto.append(get_prototype(df_a, counter_id, 6, True, type='std'))
			
			df_i = df.loc[df['mean'] < threshold]	# Select inactive days
			mean_proto = mean_proto.append(get_prototype(df_i, counter_id, 6, False, type='mean'))
			std_proto = std_proto.append(get_prototype(df_i, counter_id, 6, False, type='std'))

		bar.next()
	
	bar.finish()
	
	mean_proto.reset_index(drop=True, inplace=True), std_proto.reset_index(drop=True, inplace=True)
	mean_proto.to_pickle(OUT_PATH + 'prototypesMEAN.zip', compression='zip'), std_proto.to_pickle(OUT_PATH + 'prototypesSTD.zip', compression='zip')
