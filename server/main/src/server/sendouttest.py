import sys
import json
import numpy as np
# from pykalman import KalmanFilter
import json

family = sys.argv[1]
sensors = sys.argv[2]



with open('/app/main/static/img2/sendouttest.txt', 'w') as f:
        f.write(family + "\n")
        f.write(sensors + "\n")
