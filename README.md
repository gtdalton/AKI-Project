# AKI-Project

This is a copy of some of the work I carried out for my dissertation under supervision of Dr Daniel Bean (Kings College London) and Dr Hegler Tissot (Univeristy College London) and for the subsequent publication of a paper in additional collaboaration Christoph Boetto and Ameryic Basset (ENSTA ParisTech).
There is no patient data of any kind in this repository.

## Data requirements
The following data files are required in the following format and stored in  directory in <dataset_name>/raw_data/
(where <dataset_name> is replaced with a name for the dataset being used e.g. 'uclh')

* 'episodes.csv': demographics file (one line per ITU admission) with columns:


|Column   |Description|
|---------|-----------|
|'episode'| unique ITU admission identifier|
|'hospital_id'|unique patient identifier|
|'admission_date'|timestamp ('YYYY-MM-DD HH:MM:SS')|
|'discharge_date'|timestamp|
|'admission_age'|years (float)|
|'ethnic_group'|string|
|'gender'|string|
|'chronic_renal_replacement_therapy'|binary marker of recieving RRT for CKD during ITU stay|


"Structured Data" CSV files with the following columns:
'episode'
'hospital_id'
'value': value for data
'chartDate' timestamp for value
* heart_rate.csv
* temperature.csv
* gcs.csv
* urine_output.csv
* resp_rate.csv
* creatinine.csv (units mg/dL)

"Unstructured data" file with columns:
'episode'
'hospital_id'
'docDatei': timestamp of document
'inst': clinical concept unique identification number (CUI)
* annotations.csv


## Method
This programs labelled with the suffix 'method-' are intended to run in order to so long as they are provided the data matching thr requirements are given.  The file *uclh_file_processing.py* gets the UCLH data into the required shape

### methods_1_data_cleaning.py
Removes aberrant values specific for the variable within "Strcutured Data" csv file.  Saves files in a new folder 'cleaned_data'

### methods_2_inclusion_criteria.py
Removes episodes from the "episodes.csv" file which do not meet the inclusion criteria
NB data for non-included episodes is not removed from the "Structured Data" files in case a patient has more than one admission to ICU.  Data from excluded admissions may be used if the patient has other included admissions, e.g to calculate baseline creatinine
Output: included_episodes.csv

### methods_3_aki_algorithm.py
Input: included_episodes.csv and cleaned_data/creatinine.csv
Output: aki_episodes.csv
Processes creatinine measurements according to NHS algorithm for defining AKI

### methods_4_build_ml_input.py
Input aki_episodes, cleaned_data/*
Outut: ml_input/X_train,y_train, X_test,y_test, X_future, y_future
Creates training and validation files for given prediction intervals e.g. at 12, 24, 36, 48 and 72 hours
X_future and y_future are additional validation sets which use the most recent 10% of data as opposed to a random selection of data which X_test and y_test do

### methods_5_train_and_test.py
Input ml_input/*
Outout: ml_output/
1. Uses grid search cross-validation for hyperparameter optimisation on the training set
2. trains on whole training set with best parameters. saves a pickled model
3. tests on test set and future set.  produces performance scores, confusion matrices and roc_curves

### methods_6_model_anlysis.py
Input ml_outut/trained_model
Outout: feature importance graphs
