# AKI-Project

This is a copy of some of the work I carried out for my dissertation under supervision of Dr Daniel Bean (Kings College London) and Dr Hegler Tissot (Univeristy College London) and for the subsequent publication of a paper in additional collaboaration Christoph Boetto and Ameryic Basset (ENSTA ParisTech).
There is no patient data of any kind in this repository.

# Method
This programs labelled with the suffix 'method-' are intended to process data from start to finish.

# Data requirements
The following data files are required in the following format and stored in  directory in <dataset_name>/raw_data/
where <dataset_name> is replaced with a name for the dataset being used e.g. 'uclh'

* episodes.csv
'episode'
'hospital_id'
'admission_date'
'discharge_date'
'admission_age'
'ethnic_group'
'gender'
'chronic_renal_replacement_therapy': binary marker of recieving RRT for CKD during ITU stay


The following CSV files should have columns:
'episode': unique ITU admission identifier
'hospital_id': unique patient identifier
'value': value for data
'chartDate' timestamp for value
* heart_rate.csv
* temperature.csv
* gcs.csv
* urine_output.csv
* resp_rate.csv
* creatinine.csv (units mg/dL)

With columns
'episode'
'hospital_id'
'docDatei': timestamp of document
'inst': clinical concept unique identification number (CUI)
* annotations.csv
