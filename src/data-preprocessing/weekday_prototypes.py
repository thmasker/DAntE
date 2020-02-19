import pandas as pd
import pickle

from progress.bar import Bar


CONS_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/consumptions_byday/'
OUT_PATH = 'C:/Users/thmas/OneDrive - Universidad de Castilla-La Mancha/Informática/TFG/out/'


def get_threshold(df: pd.DataFrame) -> float:
    df.loc[:, 'mean'] = df.mean(axis=1)	# Calculate daily consumption mean
    mean, std = df['mean'].mean(), df['mean'].std()
    
    return mean + 2 * std	# Calculate threshold based on sundays

def get_prototype(df: pd.DataFrame, counter_id: int, weekday: int, active: bool) -> pd.DataFrame:
    df = df.drop(columns=['mean'])
    df = df.mean(axis=0)	# Calculate hour mean
    df = pd.DataFrame(df).T
    df.insert(0, 'active', active)
    df.insert(0, 'weekday', weekday)
    df.insert(0, 'building_id', counter_id)
    
    return df

if __name__ == '__main__':
	counters = pickle.load(open(OUT_PATH + 'counter_ids.pickle', 'rb'))
	
	bar = Bar('Collecting data', max=len(counters))
	prototypes = pd.DataFrame()
	for counter_id in counters:
		raw_df = pd.read_pickle(CONS_PATH + 'counter_' + str(counter_id) + '_byDay.zip')
		
		clean_df = raw_df.dropna()
		sundays = clean_df[clean_df.index.weekday == 6]	# Select Sundays
		threshold = get_threshold(sundays)

		prototypes = prototypes.append(get_prototype(sundays, counter_id, 6, False))	# Get Sundays prototype
		for i in range(0, 6):
			df = clean_df[clean_df.index.weekday == i]
			df.loc[:, 'mean'] = df.mean(axis=1)	# Calculate daily consumption mean
			
			df_a = df.loc[df['mean'] >= threshold]	# Select active days
			prototypes = prototypes.append(get_prototype(df_a, counter_id, i, True))
			
			df_i = df.loc[df['mean'] < threshold]	# Select inactive days
			prototypes = prototypes.append(get_prototype(df_i, counter_id, i, False))

		bar.next()
	
	bar.finish()

	prototypes.to_pickle(OUT_PATH + '/prototypes.zip', compression='zip')
