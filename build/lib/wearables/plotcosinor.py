def plotcosinor(data, transform, device):

    from wearables import fitcosinor
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import datetime as dt


    transforms = ['hill', 'antilogistic', 'arctangent']
    if transform not in transforms:
        raise ValueError("Invalid transform type. Expected one of: %s" % transforms)

    from matplotlib import rcParams
    rcParams['figure.figsize'] = (10, 8)
    rcParams['legend.fontsize'] = 16
    rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.Dark2.colors)

    params, x, y = fitcosinor.fitcosinor(data, transform)

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
        y_tx = hillfx(x.tolist(), *params.values)
    elif transform == 'antilogistic':
        y_tx = antilogfx(x, *params.values[0])
    elif transform == 'arctangent':
        y_tx = arctanfx(x.tolist(), *params)
    else:
        print('invalid transform type; exiting')


    f = plt.figure()
    plt.plot(x, y, label='%s raw' % (device.capitalize()))
    plt.plot(x, y_tx, label='%s transform' % (transform.capitalize()), linewidth = 3)
    plt.xlabel('$t$')
    plt.ylabel('LMAXACT')
    plt.legend()

    return plt
