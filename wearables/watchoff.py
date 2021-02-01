def watchoff(record_id, data, in_file, out_dir):

    import pandas as pd
    import numpy as np

    missing = pd.DataFrame([])
    out_file_new = out_dir + 'withnulls/' + infile.split('/')[-1].split('.csv')[0] + '_withnulls.csv'

for record_id in fit.keys():
    print(record_id)

    if 'beiwe' in in_file:
        hrFile = glob.glob(data_dir + 'fitbit/*%s*heartrate_1min_beiwe.csv' % record_id[0:5])[0]

    else:
        try:
            hrFile = glob.glob(data_dir + 'fitbit/WA_' + record_id[0:5] + '*heartrate_1min_' + ('[0-9]' * 3) + '*.csv')[0]

        except Exception as e:
            print(e)

    print('reading HR file %s to determine fitbit watch off times' % hrFile)

    try:
        df = []
        missingValue = 0
        hr = pd.read_csv(hrFile, index_col = 'Time', parse_dates = True)

        df = pd.merge(data, hr, left_on = 'Time', right_on = 'Time', left_index=True)

        df['Activity'][df['Value'] == 0] = np.nan

        df.to_csv(out_file_new)

        with open(out_dir + 'withnulls/fitbit_groupqc.csv','a') as missingFile:
            missingFile.write([record_id, in_file, out_file, missingValue])

        data = df['Activity']

    except Exception as e:
        print(e)
        
        return df
