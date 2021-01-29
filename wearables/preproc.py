def preproc(in_file, out_dir, device, sr, recording_period_min, interpolate_limit, truncate=False, write=False):
    import os
    from datetime import date
    import pandas as pd
    import datetime as dt
    import logging

    data = []

    try:
        today = date.today()

        if not os.path.isdir(out_dir):
            print("created output directory %s" % (out_dir))
            os.mkdir(out_dir)

        devices = ['fitbit', 'actiwatch']

        logger = logging.getLogger(__name__)
        f_handler = logging.FileHandler(out_dir + '/preproc_' + str(recording_period_min) + '_days.log')
        logger.addHandler(f_handler)
        #logging.basicConfig(filename=log_file, filemode='x', format='%(asctime)s - %(message)s', level=logging.INFO)


        if device == 'actiwatch':

            record_id = str.split(in_file, "/")[-1][0:5]

            with open(in_file) as f:
                for i, l in enumerate(f):
                    if ' Epoch-by-Epoch Data ' in l:
                        try:
                            data = pd.read_csv(in_file, skiprows = i+11, usecols = [1,2,3])
                            print('successfully read Actiware data file')
                        except:
                            try:
                                data = pd.read_csv(in_file, skiprows = i+12, usecols = [1,2,3])
                                print('successfully read Actiware data file')
                            except:
                                print('unable to read Actiware data file')

                        break

            data['Time'] = data['Date'] + ' ' + data['Time']
            data['Time'] = pd.to_datetime(data['Time'])

        elif device == 'fitbit':

            record_id = str.split(in_file, "/")[-1][3:8]

            data = pd.read_csv(in_file)
            data.columns = ['Time', 'Activity']
            data['Time'] = pd.to_datetime(data['Time'])

        else:
            raise ValueError("Invalid device type. Expected one of: %s" % devices)

        print('record %s' % (record_id))

        out_file = os.path.join(out_dir, record_id + '.csv')

        data.index = data['Time']
        data = data.resample(sr).sum()
        data = data['Activity']

        start_time = data.first_valid_index()
        end_time = data.last_valid_index()
        period = end_time - start_time

        missingNum = data.isnull().sum()
        error = 0
        logging.info('%s processing' % record_id)

        if missingNum > 0:
            # remove trailing and leading activity values
            length_init = len(data)
            data = data.loc[data.first_valid_index():data.last_valid_index()]

            logging.info('----- removed leading and trailing NaN activity values')
            missingNum = data.isnull().sum()

        if missingNum > 0:
            # interpolate up to 5 minute periods
            data.interpolate(limit=interpolate_limit, inplace=True)
            logging.info('----- interpolated')
            missingNum = data.isnull().sum()

        if missingNum > 0.10 * len(data):
            print('----- error: missing values = %s percent' %
                  (missingNum / len(data)))
            logging.warning(
                '----- discard: missing more than 10 percent of data, %s percent missing' % (missingNum / len(data)))
            error = error + 1

        if period < dt.timedelta(days=recording_period_min):
            print('----- error: less than %s days actigraphy data' %
                  (str(recording_period_min)))
            logging.warning('----- discard: insufficient recording period %s' %
                            (str(recording_period_min)))
            error = error + 1

        # truncating to first ndays of data
        if truncate == True:
            data = data[data.index < (start_time +
                        dt.timedelta(days=recording_period_min) - dt.timedelta(seconds=30))]
            end_time = data.last_valid_index()
            period = end_time - start_time
            logging.info('----- truncated recording period')

        if missingNum > 0:
            print('... error: after processing, still missing %s values' %
                  (missingNum))
            logging.warning(
                '----- error: missing %s values after processing' % missingNum)
            error = error + 1

        if error == 0:
            print('----- saving')
            logging.info('----- success: %d percent NaN, %s recording period' %
                         ((missingNum / len(data)), str(period)))
            if write == True:
                data.to_csv(out_file, index=True, index_label=None, header=None)

            print('----- success: %d percent NaN, %s recording period' %
                  ((missingNum / len(data)), str(period)))
        else:
            print('----- exclude from analysis')

    except:
        print('unable to preprocess subject %s' % record_id)

    return data
