def clockfill(data, record_id, out_dir, clockplot=True, interpolateplot=True):
    import pandas as pd
    import datetime as dt
    import matplotlib.pyplot as plt
    import os

    clocktime = [int(dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").time().strftime("%H")) + (int(
        dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").time().strftime("%M")) / 60) for x in data.index.astype(str)]
    df = pd.concat([data.reset_index(), pd.DataFrame(clocktime)],
                   axis=1, ignore_index=True)
    df.columns = ['Time', 'Activity', 'Clocktime']
    df = df.set_index(['Time'])

    if not os.path.isdir(out_dir + '/clockfill/'):
        os.makedirs(out_dir + '/clockfill/')

    df.to_csv(out_dir + '/clockfill/' + record_id + '_clockfill.csv',
              index=True, index_label=None, header=None, na_rep='NaN')

    if clockplot == True:
        if not os.path.isdir(out_dir + '/figures/'):
            os.makedirs(out_dir + '/figures/')
        p = plt.figure()
        plt.plot(df.groupby('Clocktime').mean())
        plt.title('Mean Activity Values by Minute \n%s' % record_id)
        plt.savefig(out_dir + '/figures/%s_clockplot.png' % record_id, dpi=300)
        plt.close('all')

    if interpolateplot == True:
        if not os.path.isdir(out_dir + '/figures/'):
            os.makedirs(out_dir + '/figures/')
        p = plt.figure()
        plt.plot(df.index, df.groupby('Clocktime').transform(
            lambda x: x.fillna(x.mean())))
        plt.plot(df.index, df['Activity'])
        plt.title('Raw and Clockfill Activity Values \n %s' % record_id)
        plt.savefig(out_dir + '/figures/%s_clocktimefill_plot.png' % record_id, dpi=300)
        plt.close('all')

        return df
