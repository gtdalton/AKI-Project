"""
Author @Tom
Important - this code processes a dataframe of epiosde AFTER episodes with <2 all_creatinines
and high admission creatinines have been excluded.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from methods_1_data_cleaning import set_data_set
from collections import defaultdict
import time

# Input
data_set = set_data_set()
included_episodes = pd.read_csv(data_set + 'included_episodes.csv', parse_dates =['admission_date','discharge_date'])
all_creatinines = pd.read_csv(data_set + 'cleaned_data/creatinine.csv', parse_dates = ['chartTime'])

# Output
output_file = data_set + 'aki_episodes.csv'

#crete empty lists to save aki results
episodes = []
times = []
aki_outcomes=[]

#for each unique patient in the data set, create a mini DataFrame of their episodes,
#use this to create a mini dataFrame of their creatinine measurments, indexed by date

start_time = time.time()

for row_index, row in included_episodes.iterrows():
    episode = row['episode']
    hospital_id = row['hospital_id']
    # create list of all episodes for that hospital_id
    patient_episodes = included_episodes[included_episodes['hospital_id']==hospital_id]['episode'].values
    #create df of all creatinines for that hospital_id
    patient_creatinines = all_creatinines[all_creatinines['episode'].isin(patient_episodes)].copy()
    patient_creatinines.set_index('chartTime', inplace=True)
    patient_creatinines.sort_index(inplace=True)

    #the following code creates a reference value and a time interval since the
    #previous result, for each creatinine value
    reference_values = []
    previous_result_intervals = []
    for date in patient_creatinines.index:
        df = patient_creatinines[:date]
        if df.shape[0] == 1:
            #the first ever value has no reference value
            reference_values.append(np.nan)
            previous_result_intervals.append(np.nan)
        else:
            #if the previous value is in the last 7 days, take the minumum from the last 7 days
            previous_result_interval = df.index[-1] - df.index[-2]  #this is recorded for use in defining AKI 1 later
            previous_result_intervals.append(previous_result_interval)

            previous_result_interval_days = df.index[-1].date() - df.index[-2].date()  #algorithm uses 0-7 days and 8-365 days.  Use calendar days to prevent confusion if the interval is 7.5 days
            if previous_result_interval_days  <= pd.Timedelta('7 days'):
                min_value = df.loc[date.date() - pd.Timedelta('7days'):,'value'].min()
                reference_values.append(min_value)
            #if the previous value is 8-365 days, take the median from that time
            elif previous_result_interval_days <= pd.Timedelta('365 days'):
                median_value = df.loc[date.date() - pd.Timedelta('365days'):,'value'].median()
                reference_values.append(median_value)
            else:
                # previous result is more than a year ago - ie must be previous episode
                # print('Previous result for %s at %s more than 1 year ago' %(hospital_id, date))
                reference_values.append(np.nan)
    patient_creatinines['reference_value'] = reference_values
    patient_creatinines['previous_result_interval'] = previous_result_intervals
    #the reference value can be used to calculate the RV ratio for each creatinine result
    patient_creatinines['rv_ratio'] = patient_creatinines['value']/patient_creatinines['reference_value']
    # delta is the absolute difference
    patient_creatinines['delta'] = patient_creatinines['value'] - patient_creatinines['reference_value']
    # aki1 below is not strictly accurate in all cases, so would need improving is used
    #patient_creatinines['aki1'] = (patient_creatinines['rv_ratio']>=1.5) | ((patient_creatinines['delta'] > 26) & (patient_creatinines['previous_result_interval'] < pd.Timedelta('48 hours')))
    patient_creatinines['aki2'] = patient_creatinines['rv_ratio']>=2
    patient_creatinines['aki3'] = (patient_creatinines['rv_ratio']>=3) | (patient_creatinines['value'] > 354)
    patient_creatinines['aki'] = (patient_creatinines['aki2']) | (patient_creatinines['aki3'])

    episode_creatinines = patient_creatinines[patient_creatinines['episode']==episode].copy()
    episodes.append(episode)
    # If any creatinines meet criteria for AKI, episode is labelled as AKI
    if episode_creatinines['aki'].sum()>0:
        aki_outcomes.append(1)
        # use time of first creatinine to score as aki
        times.append(episode_creatinines[episode_creatinines['aki']==True].index[0])
    # Else episode labelled as not AKI
    else:
        #use discharge time
        aki_outcomes.append(0)
        times.append(row['discharge_date'])

    if row_index %500 == 0:
        print("processed %s%% in %s seconds ---" % (row_index/included_episodes.shape[0]*100, time.time() - start_time))


aki_df = pd.DataFrame({'episode':episodes,'aki':aki_outcomes,'time':times})
aki_df.to_csv(output_file, index=False)

assert included_episodes.shape[0] == aki_df.shape[0], "Some episodes lost"
print('All included episodes classified as AKI/non-AKI')
print('%s % of patients labelled as AKI' %(aki_df['aki'].sum()/aki_sd.shape[0]*100))
