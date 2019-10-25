import pandas as pd
import glob
import os

"""Converts UCLH csv files in /data into files of required format"""

def read_all_files(extension):
    """Extension needs to be the final section of a file name which is unique for different
    file types, but constant acorss diferent semesters (plus suffix)
    e.g. extension = 'episode.csv'
    will find all files from 2014B -2018A that end ...episode.csv
    This function is required as there are many CSV files from UCLH:
    Two semesters each year from 2014B -2018A
    This function uses globbing to find all the files, then concatanates all files
    If no files are found (because the program is not being run on the UCLH server, then look for sample files)
    I have created sample CSV files just using Excel
    NB/ globbing creates a list of filenames matching pattern in random order"""


    try:
        # Use globbing to locate all files in the folder with correct ending
        csv_files = glob.glob('data/*'+extension)
        # Create an (empty) list of DataFrames
        all_semesters = []
        for file in csv_files:
            all_semesters.append(pd.read_csv(file))
        df =  pd.concat(all_semesters, ignore_index=True).sort_values('episode')
        print('Loaded UCLH %s files'%(extension))
    except:
        # If did not work, ie. could not find csv files, look in sample data folder instead
        # (This is just for code development purposes)
        df = pd.read_csv(glob.glob('sample_ucl_data/*'+extension)[0])
        print('Loaded sample %s file'%(extension))

    if 'admission_date' in df.columns.values:
        df['admission_date'] = pd.to_datetime(df['admission_date'])
        print('Data from %s to %s' %(df['admission_date'].min(), df['admission_date'].max()))
    if 'chartTime' in df.columns.values:
        print('Data from %s to %s' %(df['chartTime'].min(), df['chartTime'].max()))
        df['chartTime'] = pd.to_datetime(df['chartTime'])
    return df

def read_similar_files(files):
    """Concatenates files of the same structure e.g. temperature-central and temperature_non-central"""
    all_files = []
    for file in files:
        all_files.append(read_all_files(file))
    return pd.concat(all_files, ignore_index=True).drop_duplicates().sort_values(['episode'])

def process_episode(output_folder):
    """episode requires merging of two files - episodes and episodes extra"""
    episodes = read_all_files('episode.csv')
    #add additional columns from episode-extra
    extra = read_all_files('episode-extra.csv')[['episode','chronic_renal_replacement_therapy','weight']]
    episodes = pd.merge(episodes,extra,how='outer', on ='episode')
    episodes = episodes.sort_values('admission_date')
    # convert length_of_stay from minutes (int) to timedelata
    episodes['length_of_stay'] = episodes['length_of_stay'].apply(lambda x: pd.Timedelta(minutes=x))

    # Add discharge date columns
    episodes['discharge_date'] = episodes['admission_date'] + episodes['length_of_stay']

    episodes.to_csv(output_folder + 'episodes.csv', index=False)

def process_gcs_csv(output_folder):
    """Some GCS Data is stored only as total score (/15),
    and some is only stored as breakdown score for eye, motor and vision
    (GCS was mispelt in original files)"""
    gcs_total = read_all_files('gsc_total.csv')
    gcs_motor = read_all_files('gsc_motor.csv')
    gcs_verbal= read_all_files('gsc_verbal.csv')
    gcs_eyes = read_all_files('gsc_eyes.csv')

    # Rename 'value' column so that column names are distinct for merge
    gcs_motor.columns.values[3] = 'motor'
    gcs_verbal.columns.values[3] = 'verbal'
    gcs_eyes.columns.values[3] = 'eyes'

    # Merge three into one: gcs_agg
    gcs_agg = pd.merge(gcs_motor,gcs_verbal, on=['episode','encounter','chartTime'],how='outer')
    gcs_agg = pd.merge(gcs_agg,gcs_eyes, on=['episode','encounter','chartTime'],how='outer')

    # could impute missing values
    # gcs_agg.fillna(value={'motor':6,'eyes':4,'verbal':5})

    #calculate total for rows with all 3 columns
    gcs_agg = gcs_agg.drop_na()
    gcs_agg['value'] = gcs_agg['eyes'] + gcs_agg['verbal'] + gcs_agg['motor']

    print('GCS Total has values for %s  measurments' %(gcs_total.shape[0]))
    print('GCS Agg has values for %s measurements' %(gcs_agg.shape[0]))
    original = gcs_total.shape[0]
    gcs_total = pd.concat((gcs_total, gcs_agg[['episode','encounter','chartTime','value']]),ignore_index=True).drop_duplicates()

    print('%s more GCS measurments after combinining and removing duplicates' %((gcs_total.shape[0] - original)))
    gcs_total.to_csv(output_folder + 'gcs.csv', index=False)

def process_hr_csv(output_folder):
    hr = read_all_files('heart_rate.csv')
    hr.to_csv(output_folder + 'heart_rate.csv', index=False)

def process_temperature_csv(output_folder):
    temp = read_similar_files(['temp_central.csv', 'temp_non_central.csv'])
    temp.to_csv(output_folder + 'temperature.csv', index=False)

def process_resp_csv(output_folder):
    resp = read_similar_files(['spontaneous_resp_rate.csv','resp_rate_monitor.csv','resp_rate_vent.csv','mandatory_resp_rate.csv'])
    resp.to_csv(output_folder + 'resp_rate.csv', index=False)

def process_urine_csv(output_folder):
    urine = read_all_files('urine_output.csv')
    urine.to_csv(output_folder + 'urine_output.csv', index=False)

def process_creatinine(output_folder):
    """convert units"""
    creatinine = read_all_files('real-creatinine.csv')
    #convert units
    creatinine['value'] = creatinine['value']/84
    creatinine.to_csv(output_folder + 'creatinine.csv', index=False)

def process_blood_pressure_csv(output_folder):
    diastolic = read_all_files('diastolic.csv')
    diastolic.to_csv(output_folder + 'diastolic_blood_pressure.csv', index=False)
    systolic = read_all_files('systolic.csv')
    systolic.to_csv(output_folder + 'systolic_blood_pressure.csv', index=False)


def process_annotations(output_folder):
    annotations = read_all_files('annotations.csv')
    annotations.to_csv(output_folder + 'annotations.csv', index=False)


def add_hospital_id_to_data(output_folder, data_csv):
    """Adds hospital_id to files once they have been created by 'process_...' """
    df = pd.read_csv(output_folder + data_csv)
    episodes = pd.read_csv(output_folder + 'episodes.csv')
    df = pd.merge(df, episodes[['episode','hospital_id']], on='episode')
    df.to_csv(output_folder + data_csv, index=False)

def add_hospital_id_to_all(output_folder):
    """Adds hospital id to all data files"""
    data_fields = ['heart_rate','temperature','gcs','urine_output','resp_rate','creatinine','annotations','systolic_blood_pressure','diastolic_blood_pressure']
    for data in data_fields:
        add_hospital_id_to_data(output_folder, data + '.csv')




def main():
    output_folder = "uclh_data/raw_data/"
    if not (os.path.isdir("./"+output_folder)):
        os.mkdir(output_folder)

    process_episode(output_folder)
    process_hr_csv(output_folder)
    process_urine_csv(output_folder)
    process_temperature_csv(output_folder)
    process_gcs_csv(output_folder)
    process_resp_csv(output_folder)
    process_blood_pressure_csv(output_folder)
    process_creatinine(output_folder)
    process_annotations(output_folder)
    add_hospital_id_to_all(output_folder)



if __name__=='__main__':
    main()
