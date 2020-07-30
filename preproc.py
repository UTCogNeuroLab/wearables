def preproc(in_file, out_dir, recording_period_min, interpolate_limit, truncate=False):
    import os
    from datetime import date
    import pandas as pd
    import datetime as dt
    import logging

    today = date.today()

    log_file = os.path.join(out_dir, 'logs', 'log_' + str(dt.datetime.now().date()) +'.txt')
    logging.basicConfig(filename=log_file, filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

    record_id = in_file[0:5]
    print('record %s' % record_id)

    actig_file = os.path.join(in_dir, in_file)
    out_file = os.path.join(out_dir, record_id + '.csv')

    data = pd.read_csv(actig_file, skiprows=22, usecols=[1, 2, 3])
    data['Time'] = data['Date'] + ' ' + data['Time']
    data['Time'] = pd.to_datetime(data['Time'])
    data.index = data['Time']
    data = data['Activity']

    start_time = data.first_valid_index()
    end_time = data.last_valid_index()
    period = end_time - start_time

    missingNum = data.isnull().sum()
    error = 0
    logging.info('%s processing' % record_id)

    if missingNum > 0:
        #remove trailing and leading activity values
        length_init = len(data)
        data = data.loc[data.first_valid_index():data.last_valid_index()]

        logging.info('----- removed leading and trailing NaN activity values')
        missingNum = data.isnull().sum()

    if missingNum > 0:
        #interpolate up to 5 minute periods
        data.interpolate(limit=interpolate_limit, inplace=True)
        logging.info('----- interpolated')
        missingNum = data.isnull().sum()

    if missingNum > 0.10 * len(data):
        print('----- error: missing values = %s percent' % (missingNum/len(data)))
        logging.warning('----- discard: missing more than 10 percent of data, %s percent missing' % (missingNum/len(data)))
        error = error + 1

    if period < dt.timedelta(days = recording_period_min):
        print('----- error: less than %s days actigraphy data' % (str(recording_period_min)))
        logging.warning('----- discard: insufficient recording period %s' % (str(recording_period_min)))
        error = error + 1

    if truncate == True:
        data = data[data.index > end_time - dt.timedelta(days = recording_period_min) - dt.timedelta(seconds = 30)]
        start_time = data.index[0]
        period = end_time - start_time
        logging.info('----- truncated recording period')

    if missingNum > 0:
        print('... error: after processing, still missing %s values' % (missingNum))
        logging.warning('----- error: missing %s values after processing' % missingNum)
        error = error + 1

    if error == 0:
        print('----- saving')
        logging.info('----- success: %d percent NaN, %s recording period' % ((missingNum/len(data)), str(period)))
        data.to_csv(out_file, index=True, index_label=None, header=None)
        print('----- success: %d percent NaN, %s recording period' % ((missingNum/len(data)), str(period)))
    else:
        print('----- exclude from analysis')

    return data
