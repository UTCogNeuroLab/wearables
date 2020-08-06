def plotcosinor(paramsdf):
    import matplotlib.pyplot as plt
    rcParams['figure.figsize'] = (10, 8)
    rcParams['legend.fontsize'] = 16
    rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.Dark2.colors)

    y_act_hill = hillfx(x_act, *hill_act)

    f, ax = plt.figure()
    ax.plot(x_act, y_act, label='Actiwatch Raw')
    ax.plot(x_fit, y_fit, label='Fitbit Raw')
    ax.plot(x_fit, y_fitInt, label='Fitbit Interpolated')
    ax.plot(x_act, y_act_arctan, label='Arctangent Transform', linewidth = 3)
    ax.plot(x_fit, y_fit_arctan, label='Arctangent Transform', linewidth = 3)
    ax.plot(x_fit, y_fitInt_arctan, label='Arctangent Transform', linewidth = 3)
    ax.xlabel('$t$')
    ax.ylabel('LMAXACT')
    ax.legend(bbox_to_anchor=(1.8, 1), loc='upper right', ncol=1)

    return ax
