def fitcosinor(data, transform='antilogistic'):
    # performs cosinor analysis based on sinusoidally transformed cosine methods outlined in Marler (2006)

    import numpy as np
    import pandas as pd
    import datetime as dt

    import matplotlib.pyplot as plt

    from scipy.optimize import curve_fit
    from scipy.optimize import Bounds

    transforms = ['hill', 'antilogistic', 'arctangent']
    if transform not in transforms:
        raise ValueError("Invalid transform type. Expected one of: %s" % transforms)

    data = pd.DataFrame(data)

    data['clocktime'] = [int(dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").time().strftime("%H")) + (int(dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").time().strftime("%M"))/60) for x in data.index.astype(str)]
    data = data.groupby('clocktime').max()
    data['lmaxact'] = np.log10(data['Activity'] + 1)

    def hillfx(t, actmin, amp, phi, m, g):
        # takes 3 x: min, amp, m
        bounds = ([0, 0, 0, -np.inf, -np.inf],[2, 2, 24, np.inf, np.inf])
        c = abs(np.cos((t - phi) * (2*np.pi/24)))
        return actmin + amp*(((c+1)**g )/( m**g + (c+1)**g ))

    def antilogfx(t, actmin, amp, alpha, beta, phi):
        # takes 5 x: min, amp, alpha, beta, phi
        bounds = ([0, 0, -np.inf, 0, 0], [2, 2, np.inf, np.inf, 24])
        c = np.cos((t - phi) * (2*np.pi/24))
        return actmin + amp*((np.exp(beta * (c - alpha)))/(1 + np.exp(beta * (c - alpha))))

    def arctanfx(t, actmin, amp, alpha, beta, phi):
        # takes 5 x: min, amp, alpha, beta, phi
        bounds = ([0, 0, -np.inf, 0, 0], [2, 2, np.inf, np.inf, 24])
        c = np.cos((t - phi) * (2*np.pi/24))
        return actmin + amp*(np.arctan(beta * (c - alpha))/(np.pi + (1/2)))

    if transform == 'hill':
        params, fxcov = curve_fit(hillfx, xdata = data.index.values, ydata = data['lmaxact'].values)
    elif transform == 'antilogistic':
        params, fxcov = curve_fit(antilogfx, xdata = data.index.values, ydata = data['lmaxact'].values)
    elif transform == 'arctangent':
        params, fxcov = curve_fit(arctanfx, xdata = data.index.values, ydata = data['lmaxact'].values)
    else:
        print('invalid transform type; exiting')

    paramsdf = pd.DataFrame(params[None], columns =  [['actmin', 'amp', 'alpha', 'beta', 'phi']])

    x = data.index.values
    y = data['lmaxact'].values

    return paramsdf, x, y
