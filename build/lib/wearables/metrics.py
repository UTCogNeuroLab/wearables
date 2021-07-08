import pandas as pd
import numpy as np

# used from ghammad/pyActigraphy https://github.com/ghammad/pyActigraphy/blob/master/pyActigraphy/metrics/metrics.py

    def _interdaily_stability(data):
    r"""Calculate the interdaily stability"""

    d_24h = data.groupby([
        data.index.hour,
        data.index.minute,
        data.index.second]
    ).mean().var()

    d_1h = data.var()

    return (d_24h / d_1h)


def _intradaily_variability(data):
    r"""Calculate the intradaily variability"""

    c_1h = data.diff(1).pow(2).mean()

    d_1h = data.var()

    return (c_1h / d_1h)


def _lmx(data, period, lowest=True):
    """Calculate the start time and mean activity of the period of
    lowest/highest activity"""

    avgdaily = _average_daily_activity(data=data, cyclic=True)

    n_epochs = int(pd.Timedelta(period)/avgdaily.index.freq)

    mean_activity = avgdaily.rolling(period).sum().shift(-n_epochs+1)

    if lowest:
        t_start = mean_activity.idxmin()
    else:
        t_start = mean_activity.idxmax()

    lmx = mean_activity[t_start]/n_epochs
    return t_start, lmx

 def RA(self, binarize=True, threshold=4):
        r"""Relative rest/activity amplitude
        Relative amplitude between the mean activity during the 10 most active
        hours of the day and the mean activity during the 5 least active hours
        of the day.
        Parameters
        ----------
        binarize: bool, optional
            If set to True, the data are binarized.
            Default is True.
        threshold: int, optional
            If binarize is set to True, data above this threshold are set to 1
            and to 0 otherwise.
            Default is 4.
        Returns
        -------
        ra: float
        Notes
        -----
        The RA [1]_ variable is calculated as:
        .. math::
            RA = \frac{M10 - L5}{M10 + L5}
        References
        ----------
        .. [1] Van Someren, E.J.W., Lijzenga, C., Mirmiran, M., Swaab, D.F.
               (1997). Long-Term Fitness Training Improves the Circadian
               Rest-Activity Rhythm in Healthy Elderly Males.
               Journal of Biological Rhythms, 12(2), 146–156.
               http://doi.org/10.1177/074873049701200206
        Examples
        --------
            >>> import pyActigraphy
            >>> rawAWD = pyActigraphy.io.read_raw_awd(fpath + 'SUBJECT_01.AWD')
            >>> rawAWD.RA()
            0.XXXX
            >>> rawAWD.RA(binarize=False)
            0.XXXX
        """

        if binarize is True:
            data = self.binarized_data(threshold)
        else:
            data = self.data

        # n_epochs = int(pd.Timedelta('5H')/self.frequency)

        _, l5 = _lmx(data, '5H', lowest=True)
        _, m10 = _lmx(data, '10H', lowest=False)

        return (m10-l5)/(m10+l5)

    def L5p(self, period='7D', binarize=True, threshold=4, verbose=False):
        r"""L5 per period
        The L5 variable is calculated for each consecutive period found in the
        actigraphy recording.
        Parameters
        ----------
        period: str, optional
            Time period for the calculation of IS
            Default is '7D'.
        binarize: bool, optional
            If set to True, the data are binarized.
            Default is True.
        threshold: int, optional
            If binarize is set to True, data above this threshold are set to 1
            and to 0 otherwise.
            Default is 4.
        verbose: bool, optional
            If set to True, display the number of periods found in the activity
            recording, as well as the time not accounted for.
            Default is False.
        Returns
        -------
        l5p: list of float
        Notes
        -----
        The L5 [1]_ variable is calculated as the mean, per acquisition period,
        of the average daily activities during the 5 least active hours.
        .. warning:: The value of this variable depends on the length of the
                     acquisition period.
        References
        ----------
        .. [1] Van Someren, E.J.W., Lijzenga, C., Mirmiran, M., Swaab, D.F.
               (1997). Long-Term Fitness Training Improves the Circadian
               Rest-Activity Rhythm in Healthy Elderly Males.
               Journal of Biological Rhythms, 12(2), 146–156.
               http://doi.org/10.1177/074873049701200206
        Examples
        --------
            >>> import pyActigraphy
            >>> rawAWD = pyActigraphy.io.read_raw_awd(fpath + 'SUBJECT_01.AWD')
            >>> rawAWD.duration()
            Timedelta('12 days 18:41:00')
            >>> rawAWD.L5p(period='5D',verbose=True)
            Number of periods: 2
            Time unaccounted for: 2 days, 19h, 0m, 0s
            [0.XXXX, 0.XXXX]
        """

        if binarize is True:
            data = self.binarized_data(threshold)
        else:
            data = self.data

        # n_epochs = int(pd.Timedelta('5H')/self.frequency)

        intervals = _interval_maker(data.index, period, verbose)

        results = [
            _lmx(
                data[time[0]:time[1]],
                '5H',
                lowest=True
            ) for time in intervals
        ]
        return [res[1] for res in results]

    def M10p(self, period='7D', binarize=True, threshold=4, verbose=False):
        r"""M10 per period
        The M10 variable is calculated for each consecutive period found in the
        actigraphy recording.
        Parameters
        ----------
        period: str, optional
            Time period for the calculation of IS
            Default is '7D'.
        binarize: bool, optional
            If set to True, the data are binarized.
            Default is True.
        threshold: int, optional
            If binarize is set to True, data above this threshold are set to 1
            and to 0 otherwise.
            Default is 4.
        verbose: bool, optional
            If set to True, display the number of periods found in the activity
            recording, as well as the time not accounted for.
            Default is False.
        Returns
        -------
        m10p: list of float
        Notes
        -----
        The M10 [1]_ variable is calculated as the mean, per acquisition period
        , of the average daily activities during the 10 most active hours.
        .. warning:: The value of this variable depends on the length of the
                     acquisition period.
        References
        ----------
        .. [1] Van Someren, E.J.W., Lijzenga, C., Mirmiran, M., Swaab, D.F.
               (1997). Long-Term Fitness Training Improves the Circadian
               Rest-Activity Rhythm in Healthy Elderly Males.
               Journal of Biological Rhythms, 12(2), 146–156.
               http://doi.org/10.1177/074873049701200206
        Examples
        --------
            >>> import pyActigraphy
            >>> rawAWD = pyActigraphy.io.read_raw_awd(fpath + 'SUBJECT_01.AWD')
            >>> rawAWD.duration()
            Timedelta('12 days 18:41:00')
            >>> rawAWD.M10p(period='5D',verbose=True)
            Number of periods: 2
            Time unaccounted for: 2 days, 19h, 0m, 0s
            [0.XXXX, 0.XXXX]
        """

        if binarize is True:
            data = self.binarized_data(threshold)
        else:
            data = self.data

        # n_epochs = int(pd.Timedelta('10H')/self.frequency)

        intervals = _interval_maker(data.index, period, verbose)

        results = [
            _lmx(
                data[time[0]:time[1]],
                '10H',
                lowest=False
            ) for time in intervals
        ]
        return [res[1] for res in results]
