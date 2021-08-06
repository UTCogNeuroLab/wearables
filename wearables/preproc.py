def preproc(in_file, device, sr='1T', start_time_csv='None', end_time_csv='None', truncate=True, write=True, plot=True, recording_period_min=7, interpolate_method='linear', interpolate_limit=10):
    import os
    import sys
    import linecache
    from datetime import date
    import pandas as pd
    import datetime as dt
    import logging
    import glob
    import matplotlib.pyplot as plt
    from wearables import watchoff
    import numpy as np
    """
    in_file is _New_Analysis.csv raw Actiware export
    device is either 'actiwatch' or 'fitbit'
    sr is 1T for 1 minute, 0.5T for 30 seconds, etc.
    start_time_csv and end_time_csv default to 'None'. These are csv files with record id (3 digit from redcap) and start or end time for actigraphy data collection. Must have both or neither files.
    truncate will take the first n days of Data
    write writes out csv files for each of the preprocessing steps (truncate, interpolate)
    plot generates plots comparing the raw data to the preprocessed Data
    recording period min specifies the number of days to truncate to/minimum days of activity Data
    interpolate limit is number of epochs to interpolate (1T with interpolate_limit=10 is 10 min, 0.5T with interpolate_limit=20 is 10 min)
    interpolate method defaults to linear
    """

    def PrintException():
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(
            filename, lineno, line.strip(), exc_obj))

    data = []

    try:
        today = date.today()

        out_dir = os.path.dirname(in_file) + '/preproc_%s/' % today

        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
            print("created output directory %s" % (out_dir))

        devices = ['fitbit', 'actiwatch']

        logger = logging.getLogger(__name__)
        f_handler = logging.FileHandler(
            out_dir + str(recording_period_min) + '_days.log')
        logger.addHandler(f_handler)
        # logging.basicConfig(filename=log_file, filemode='x', format='%(asctime)s - %(message)s', level=logging.INFO)

        if device == 'actiwatch':

            record_id = str(os.path.basename(in_file)).split('_')[0]

            with open(in_file) as f:
                for i, l in enumerate(f):
                    if ' Epoch-by-Epoch Data ' in l:
                        try:
                            data = pd.read_csv(
                                in_file, skiprows=i + 11, usecols=[1, 2, 3])
                            print('successfully read Actiware data file')
                        except:
                            try:
                                data = pd.read_csv(
                                    in_file, skiprows=i + 12, usecols=[1, 2, 3])
                                print('successfully read Actiware data file')
                            except:
                                print('unable to read Actiware data file')

                        break

            data['Time'] = data['Date'] + ' ' + data['Time']
            data['Time'] = pd.to_datetime(data['Time'])

        elif device == 'fitbit':

            record_id = os.path.basename(in_file).split("WA_")[1][0:5]

            data = pd.read_csv(in_file)
            data.columns = ['Time', 'Activity']
            data['Time'] = pd.to_datetime(data['Time'])

        else:
            raise ValueError(
                "Invalid device type. Expected one of: %s" % devices)

        print('record %s' % (record_id))

        data.index = data['Time']
        data = data.resample(sr).sum()
        data = data['Activity']

        if (start_time_csv == 'None') & (end_time_csv == 'None'):

            if device == 'fitbit':
                # data = watchoff.watchoff(record_id, data, in_file, out_dir)
                start_time = data.first_valid_index()
                end_time = data.last_valid_index()

            elif device == 'actiwatch':
                start_time = data.index[np.nonzero(data.values)[0][0]]
                end_time = data.index[np.nonzero(data.values)[0][-1]]
        else:
            start_times = pd.read_csv(
                start_time_csv, header=None, dtype=str, parse_dates=True)
            start_times[[0]] = start_times[[0]].apply(
                lambda x: x.astype(str).str.zfill(3))
            start_time = pd.to_datetime(start_times.where(start_times[0] == record_id[-3:]).dropna()[1]).to_list()

            end_times = pd.read_csv(
                end_time_csv, header=None, dtype=str, parse_dates=True)
            end_times[[0]] = end_times[[0]].apply(
                lambda x: x.astype(str).str.zfill(3))
            end_time = pd.to_datetime(end_times.where(end_times[0] == record_id[-3:]).dropna()[1]).to_list()

            if (len(start_time) != 2):

                start_time = pd.to_datetime(start_time[0])
                end_time = pd.to_datetime(end_time[0])

            else:

                if ((start_time[0] < data.head(1).index)[0] | (start_time[0] > data.tail(1).index)[0]):

                    start_time = pd.to_datetime(start_time[1])
                    end_time = pd.to_datetime(end_time[1])

                else:
                    
                    start_time = pd.to_datetime(start_time[0])
                    end_time = pd.to_datetime(end_time[0])

            period = int(((end_time - start_time)/np.timedelta64(1, 'D')))

        if period < recording_period_min:
            print('----- error: less than %s days actigraphy data - recording period is %s ' %
                  (str(recording_period_min), str(period)))
            logging.warning('----- discard: insufficient recording period %s' %
                            (str(period)))
            error = error + 1

        else:

            raw = data

            missingNum = data.isnull().sum()
            error = 0
            logging.info('%s processing' % record_id)

            if not in_file.endswith('_beiwe.csv'):
                data = data[start_time:end_time]
                logging.info(
                    '----- removed leading and trailing NaN activity values')

            print('%s missing %s values out of %s total (%.2f percent)' % (
                record_id, data.isnull().sum(), len(data), data.isnull().sum() / len(data) * 100))

            if missingNum > 0.20 * len(data):
                print('----- error: missing values = %.2f percent' %
                      (100 * (missingNum / len(data))))
                logging.warning(
                    '----- discard: missing more than 10 percent of data, %.2f percent missing' % (missingNum / len(data) * 100))
                error = error + 1

            else:
                if missingNum > 0:
                    new_data = data.interpolate(
                        method=interpolate_method, limit=interpolate_limit, inplace=True, limit_area='inside')
                    data.update(new_data)
                    logging.info('----- interpolated with %s, limit = %s' %
                                 (interpolate_method, interpolate_limit))
                    if not os.path.isdir(out_dir + '/interpolated/'):
                        os.makedirs(out_dir + '/interpolated/')
                    data.to_csv(out_dir + '/interpolated/%s_%s-d_interpolated-method-%s_lim-%s-epoch.csv' % (record_id, recording_period_min,
                                interpolate_method, interpolate_limit), index=True, index_label=None, header=None, na_rep='NaN')
                    missingNum = data.isnull().sum()

                print('interpolated - now missing %s values out of %s total (%s percent)' %
                      (data.isnull().sum(), len(data), data.isnull().sum() / len(data) * 100))

                # truncating to first ndays of data
                if truncate == True:
                    data = data[data.index <= (start_time + dt.timedelta(seconds=30) +
                                               dt.timedelta(days=recording_period_min))]
                    end_time = data.last_valid_index()
                    period = end_time - start_time
                    logging.info(
                        '----- truncated recording period to %s days' % recording_period_min)
                    missingNum = data.isnull().sum()
                    if not os.path.isdir(out_dir + '/truncated/'):
                        os.makedirs(out_dir + '/truncated/')
                    data.to_csv(out_dir + 'truncated/%s_interpolated_truncated-%s-d.csv' % (record_id,
                                recording_period_min), index=True, index_label=None, header=None, na_rep='NaN')
                    print(missingNum)

                if plot == True:
                    f, axs = plt.subplots(2, 1, sharex=True)
                    axs[0].plot(raw.index, raw, color='blue')
                    axs[0].set_title(record_id + ', ' +
                                     str(recording_period_min) + ' days')
                    axs[0].xaxis.set_visible(False)

                    axs[1].plot(data.index, data, color='red')
                    plt.xticks(rotation=45)
                    plt.tight_layout()

                    if not os.path.isdir(out_dir + '/figures/'):
                        os.makedirs(out_dir + '/figures/')
                    plt.savefig(out_dir + '/figures/' + record_id + '_' + str(
                        recording_period_min) + '_d_interpolate-' + interpolate_method + '.png', dpi=300)
                    plt.close()

                if missingNum > 0:
                    print('... error: after processing, still missing %.2f percent data' %
                          (100 * (missingNum / len(data))))
                    logging.warning(
                        '----- error: missing %.2f percent after processing' % (100 * (missingNum / len(data))))
                    error = error + 1

                if error == 0:
                    logging.info('----- success: %.2f percent NaN, %s recording period' %
                                 (100 * (missingNum / len(data)), str(period)))

                    print('----- success: %.2f percent NaN, %s recording period' %
                          (100 * (missingNum / len(data)), str(period)))
                else:
                    print('----- exclude from analysis')

                data.to_csv(out_dir + '/' + record_id + '_%s-d.csv' % recording_period_min,
                            index=True, index_label=None, header=None, na_rep='NaN')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('--- ERROR --- ')
        print(PrintException())
        # print(e)
        # print(exc_type, fname, exc_tb.tb_lineno)

    return data

# in_file = '/Volumes/schnyer/Megan/Wearables/data/fitbit/WA_10011_minuteStepsNarrow_20190901_20201020.csv'
# data = pd.read_csv(infile)
# sr='1T'
# start_time_csv = '/Volumes/schnyer/Megan/Wearables/data/start_times.csv'
# end_time_csv = '/Volumes/schnyer/Megan/Wearables/data/end_times.csv'
# recording_period_min=7
