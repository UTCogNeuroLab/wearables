def watchoff(record_id, data, in_file, out_dir):
    import pandas as pd
    import numpy as np
    import glob
    import csv
    import os

    missing = pd.DataFrame([])
    out_file_new = out_dir + os.path.basename(in_file).split('WA_')[1][0:5] + '_withnulls.csv'

    try:
        if 'beiwe' in in_file:
            hrFile = (glob.glob(in_file.split('fitbit/')[0] + 'fitbit/WA_' + '%s*heartrate_1min_beiwe.csv' % record_id[0:5]))[0]
        else:
            hrFile = (glob.glob(in_file.split('fitbit/')[0] + 'fitbit/WA_' + record_id[0:5] + '*heartrate_1min_' + ('[0-9]' * 3) + '*.csv'))[0]

        df = []
        missingValue = 0
        hr = pd.read_csv(hrFile, index_col='Time', parse_dates=True)

        df = pd.merge(data, hr, left_on='Time',
                      right_on='Time', left_index=True)

        df['Activity'][df['Value'] == 0] = np.nan

        df = df['Activity']
        missingValue = df.isnull().sum()/len(df)

        with open(out_dir + 'fitbit_groupqc.csv', 'a') as missingFile:
            writer=csv.writer(missingFile, delimiter=',')
            writer.writerow([record_id, in_file, out_file_new, missingValue])

    except Exception as e:
        print(e)

    return df
