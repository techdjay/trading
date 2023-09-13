datadir = "../data"

import glob
import numpy as np
import pandas as pd

for path in glob.glob(datadir+"/*"):
    for f in glob.glob(path+"/*"):
        df = pd.read_csv(f)

        df.tail(2)
        df.tail()