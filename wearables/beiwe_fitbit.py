#!/usr/bin/env python
# coding: utf-8

# Convert Beiwe files and trim to remove leading and trailing missing values

import pandas as pd
import glob
import zipfile
import os

homeDir = '/Users/PSYC-mcm5324/'
dataDir = homeDir + 'Box/Megan Fitbit data/'
outDataDir = homeDir + 'Box/CogNeuroLab/Wearables/data/fitbit/Beiwe/'


beiweFiles = glob.glob(dataDir + '*.zip')

for fileName in beiweFiles:
    print(fileName)
    subNum = fileName.split('data/')[1].split('-')[0]
    subDir = dataDir + subNum
    outFileName = outDataDir + 'WA_' + fileName.split('data/')[1].split('-')[0] + '.csv'

    if not os.path.exists(outFileName):

        if not os.path.isdir(subDir):

            # extract from Megan Fitbit data
            with zipfile.ZipFile(fileName, 'r') as zip_ref:
                zip_ref.extractall(subDir)

            # read intraday csv
            df = pd.read_csv(subDir + '/fitbit_intraday_records.csv')

            # remove leading and trailing NaN values
            dfStart = df['activities_heart'].first_valid_index()
            dfEnd = df['activities_heart'].last_valid_index()
            dfNew = df.loc[dfStart:dfEnd]
            dfNew.columns = ['Time', 'Activity']

            # save out to lab data directory
            dfNew.to_csv(outDataDir + 'WA_' + fileName.split('data/')[1].split('-')[0] + '.csv')

            print('\n saved data for subject %s. remember to remove unzippped data file from /Box/Megan Fitbit data. \n\n' % subNum)
    else:
        print('\n data for subject %s already exists in output directory. \n\n' % subNum)
