# adapted from ghammad/pyActigraphy https://github.com/ghammad/pyActigraphy
# formulas and text from Blume et al. 2016
# Isabella McConley & Megan McMahon

import pandas as pd
import numpy as np
import datetime

# data is a dataframe with time and activity values
# time is formatted as a datetime index with format = '%Y-%m-%dT%H:%M:%S'

def interdaily_stability(data):
    """IS quantifies the stability of rest-activity rhythms or the invariability
    of the rhythm betweendifferent days. It, thus, describes the coupling of the
    rhythm to external zeitgebers, that isenvironmental cues such as light that
    entrain an organism’s internal biological clock to the earth’s24 h cycle. IS
    varies between 0 (Gaussian noise) and 1 with values closer to 1 indicating
    strongercoupling to a zeitgeber with a period length of 24 h.

    Interdaily stability (IS). n is the total number of sampling points and p is
    the number ofsampling points per day while xhare the hourly means, x is the
    grand average of all data and xidenotes the activity value from each
    sampling point. (Blume et al., 2016)"""

    d_24h = data.groupby([
        data.index.hour,
        data.index.minute,
        data.index.second]
    ).mean().var()

    d_1h = data.var()

    return (d_24h / d_1h)


def intradaily_variability(data):
    """V quantifies the fragmentation of a rest-activity pattern. IV converges
    to zero for aperfect sine wave and approaches two for Gaussian noise. It may
     even be higher than two if adefinite ultradian component with a period
     length of two hours is present in the rest-activity cycle.

     Intradaily variability (IV). n is the total number of sampling points and p
     is the numberof sampling points per day x is the grand average of all data
     and xidenotes the activity value fromeach sampling point. (Blume et al., 2016)"""

    c_1h = data.diff(1).pow(2).mean()

    d_1h = data.var()

    return (c_1h / d_1h)


def _lmx(data, period, lowest=True):
     """M10 is the averaged activity of the ten consecutive hours withmaximal activity,
     L5 is the averaged activity of the five consecutive hours with minimal activity.
     To find M10 and L5 averages for ten and five hours are calculated on a
     minute-wise level across days. More precisely, minute-wise averages are first
     calculated across days. Subsequently, rolling averages for five and 10 h are
     computed. From these, the maximal value from the 10 h averages and the
     minimal value from the five hour averages are picked as well as the times
     of the day when M10 and L5 start. (Blume et al., 2016)"""

    avgdaily = data.groupby([data.index.hour, data.index.minute, data.index.second]).mean()

    avgdaily.index = avgdaily.index.rename(names = ['hour', 'minute', 'second'])
    avgdaily = avgdaily.reset_index()

    avgdailycyclic = avgdaily[avgdaily['hour'] == 23].append(avgdaily).set_index(['hour', 'minute', 'second'])

    mean_activity = avgdailycyclic.rolling(period*60).mean()

    if lowest:
        t_start = mean_activity.idxmin()
    else:
        t_start = mean_activity.idxmax()

    lmx = float(mean_activity.loc[t_start].values)
    return t_start, lmx

 def relative_amplitude(data):
     """RA is a non-parametric parameter, which can be calculated from the M10
     and L5 values, that is theten hours with maximal (M10) and the five hours
     with minimal (L5) activity. Usually, M10 covers10 h during the day and may
     be influenced by e.g. daytime napping. L5, on the other hand, should reflect
     movements during the night as well as arousals and awakenings. (Blume et al., 2016)"""

    _, l5 = _lmx(data, 5, lowest=True)
    _, m10 = _lmx(data, 10, lowest=False)

    return (m10-l5)/(m10+l5)
