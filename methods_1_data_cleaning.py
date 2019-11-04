import pandas as pd
import os, pickle

"""Removes impossible values from structured data
Removes annotations where experiencer not patient
Creates limited annotations file which only has annotatios found in MIMIC based on Christoph's cui_graph_1234 file"""

def set_data_set():
    """Set which data set to use (as may have multiple data sets on same server)"""
    print('Select dataset - MIMIC: 1 / UCLH:2\n>')
    data_set = input()
    if data_set == '1':
        return 'mimic_data/'
    elif data_set == '2':
        return 'uclh_data/'
    else:
        print('\nInvalid\n')
        return set_data_set()



def clean_gcs(input_folder,output_folder):
    """Remove GCS if above 15 or below 3"""
    df = pd.read_csv(input_folder + 'gcs.csv')

    num_measurements = df.shape[0]
    df = df[df['value']<=15]
    print('%s of %s GCS measurments above 15 removed' %(num_measurements - df.shape[0], num_measurements))

    num_measurements = df.shape[0]
    df = df[df['value']>=3]
    print('%s of %s GCS measurments less than 3 removed' %(num_measurements - df.shape[0],num_measurements))

    df.to_csv(output_folder+'/gcs.csv', index=False)

def clean_hr(input_folder,output_folder):
    """Remove heart rate if below 1"""
    df = pd.read_csv(input_folder +'heart_rate.csv')

    num_measurements = df.shape[0]
    df = df[df['value'] > 0]
    print('%s of %s heart rate measurments of 0 removed' %(num_measurements - df.shape[0],num_measurements))
    df.to_csv(output_folder+'/heart_rate.csv', index=False)

def clean_temperature(input_folder,output_folder):
    """Remove values <25 or >50"""
    df = pd.read_csv(input_folder +'temperature.csv')
    assert 36<df['value'].mean() <38, 'Check temperature units in centigrade'
    num_measurements = df.shape[0]
    df = df[df['value'] >= 25]
    print('%s of %s temperature measurments below 25 removed' %(num_measurements - df.shape[0],num_measurements))

    num_measurements = df.shape[0]
    df = df[df['value'] <= 50]
    print('%s of %s temperature measurments above 50 removed' %(num_measurements - df.shape[0],num_measurements))

    df.to_csv(output_folder+'/temperature.csv', index=False)

def clean_resp_rate(input_folder,output_folder):
    """Drop 0 values and below 0 (lots of negative values in uclh data set)"""
    df = pd.read_csv(input_folder +'resp_rate.csv')

    num_measurements = df.shape[0]
    df = df[df['value'] > 0]
    print('%s of %s resp rate measurments of 0 or negative removed' %(num_measurements - df.shape[0], num_measurements))

    df.to_csv(output_folder+'/resp_rate.csv', index=False)

def clean_urine_output(input_folder,output_folder):
    """Remove values above 1000.  This is because some urine measuremnts are recorded cummulatively
    Could be improved to identify cummulative urine output measuremnts and convert to individual num_measurements
    as 1000 is somehwat arbitary"""
    df = pd.read_csv(input_folder +'urine_output.csv')

    num_measurements = df.shape[0]
    df = df[df['value'] <= 1000]
    print('%s of %s urine output measurments above 1000 removed' %(num_measurements - df.shape[0],num_measurements))

    df.to_csv(output_folder+'/urine_output.csv', index=False)

def clean_blood_pressure(input_folder,output_folder):
    """Remove values of 0
    Could add ability to assert systolic > bp"""
    for bp in ['systolic', 'diastolic']:
        df = pd.read_csv(input_folder +'%s_blood_pressure.csv'%bp)
        num_measurements = df.shape[0]
        df = df[df['value']>0]
        print('%s of %s %s blood pressure measurments of 0 removed' %(num_measurements - df.shape[0],num_measurements, bp))
        print('Max %s: %s'%(bp, df['value'].max()))
        print('Mean %s: %s'%(bp, df['value'].mean()))
        print('Min %s: %s'%(bp, df['value'].min()))
        df.to_csv(output_folder+'%s_blood_pressure.csv'%bp, index=False)

def clean_creatinine(input_folder,output_folder):
    """Drop 0 values"""
    df = pd.read_csv(input_folder +'creatinine.csv')

    num_measurements = df.shape[0]
    df = df[df['value'] > 0]
    print('%s of %s creatinine measurments of 0 removed' %(num_measurements - df.shape[0],num_measurements))

    df.to_csv(output_folder+'/creatinine.csv', index=False)

def clean_episodes(input_folder,output_folder):
    """currently no data changed"""
    df = pd.read_csv(input_folder +'episodes.csv')
    df.to_csv(output_folder + 'episodes.csv', index=False)

def clean_annotations(input_folder, output_folder):
    """Remove annotations where Experiencer is not patient"""
    df = pd.read_csv(input_folder + 'annotations.csv')
    df = df[df['Experiencer'] == 'Patient']
    df.to_csv(output_folder + 'annotations.csv', index=False)



def main():
    data_set = set_data_set()
    input_folder =  data_set + "raw_data/"
    output_folder = data_set + "cleaned_data/"
    if not (os.path.isdir("./"+output_folder)):
        od.mkdir("./"+output_folder)

    clean_episodes(input_folder,output_folder)
    clean_hr(input_folder,output_folder)
    clean_urine_output(input_folder,output_folder)
    clean_temperature(input_folder,output_folder)
    clean_gcs(input_folder,output_folder)
    clean_resp_rate(input_folder,output_folder)
    clean_creatinine(input_folder,output_folder)
    clean_annotations(input_folder, output_folder)
    clean_blood_pressure(input_folder, output_folder)

if __name__=='__main__':
    main()
