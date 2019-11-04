import pandas as pd
from methods_1_data_cleaning import set_data_set



def inclusion_criteria(data_set, minimum_age=18,min_num_creatinine_readings=3):
    input_folder = data_set + "cleaned_data/"
    episodes = pd.read_csv(input_folder + 'episodes.csv', parse_dates=['admission_date'])

    # Remove under 18
    num_episodes = episodes.shape[0]
    episodes = episodes[episodes['admission_age']>=minimum_age]
    print('%s episodes removed as patient under 18' %(num_episodes - episodes.shape[0]))

    # Remove episodes with less than two creatinine readings
    num_episodes = episodes.shape[0]
    creatinine = pd.read_csv(input_folder + 'creatinine.csv', parse_dates = ['chartTime'])
    creatinine_value_counts = creatinine['episode'].value_counts()
    included_episodes = list(creatinine_value_counts[creatinine_value_counts >= min_num_creatinine_readings].index)
    episodes = episodes[episodes['episode'].isin(included_episodes)]
    print ('%s episodes removed as <%s creatinine readings' %(num_episodes - episodes.shape[0], min_num_creatinine_readings))

    # remove episodes with a recording of chronic renal replacement therapy
    if 'chronic_renal_replacement_therapy' in episodes.columns:
        num_episodes = episodes.shape[0]
        episodes = episodes[episodes['chronic_renal_replacement_therapy']!= 1]
        print('%s episodes removed due to chronic renal replacement therapy' %(num_episodes - episodes.shape[0]))

    # remove episodes with high admission creatinine

    episodes.to_csv(data_set + 'included_episodes.csv', index=False)

def main():
    data_set = set_data_set()
    inclusion_criteria(data_set)

if __name__=='__main__':
    main()
