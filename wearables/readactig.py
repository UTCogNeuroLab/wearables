def readactig(file):
    import pandas as pd
    # actigraphy input file is a file with two columns, Time ("%Y-%m-%d %H:%M:%S") and Activity, with no header

    data = pd.read_csv(file, sep = " ", header = None, names = ['time', 'activity'])

    return data
