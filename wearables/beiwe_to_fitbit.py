def beiwe_to_fitabase(beiwe_dir, out_dir, sr):
    import os
    import sys
    import pandas as pd
    import glob

    for beiwe_file in glob.glob(beiwe_dir + '/*.csv'):
        try:
            data = pd.read_csv(beiwe_file)
            data = data[['date', 'activities_steps']]
            data.columns = ['Time', 'Activity']
            data['Time'] = pd.to_datetime(data['Time'])
            data.index = data['Time']
            data = data.resample(sr).sum()
            print(data[0:3])

            print(out_dir + '/' + str(beiwe_file).split('/')[-1].split('.csv')[0] + '_minuteStepsNarrow.csv')
            data.to_csv(out_dir + '/' + str(beiwe_file).split('/')[-1].split('.csv')[0] + '_minuteStepsNarrow.csv', index=True, index_label=None, header=None, na_rep='NaN')

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('error with data for %s' % str(beiwe_file).split('/')[-1])
            print(e)
            print(exc_type, fname, exc_tb.tb_lineno)

beiwe_dir = '/Volumes/schnyer/Megan/Wearables/data/fitbit/beiwe'
out_dir = '/Volumes/schnyer/Megan/Wearables/data/fitbit'

beiwe_to_fitabase(beiwe_dir, out_dir, sr='1T')
