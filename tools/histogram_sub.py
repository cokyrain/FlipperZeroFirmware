import re
import sys
import pandas as pd
import matplotlib.pyplot as plt

filename = sys.argv[1]

segs = []
with open(filename, 'r') as f:
    for line in f:
        m = re.match(r'RAW_Data:\s*([-0-9 ]+)\s*$', line)
        if m:
            segs.extend(abs(int(seg)) for seg in m[1].split(r' '))

series = pd.Series(segs)

# Get rid of outliers
series = series[series < 5000]

series.plot.hist(bins=100)
plt.show()
