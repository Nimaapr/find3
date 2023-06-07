import sys
import json
import numpy as np
# from pykalman import KalmanFilter
import json

family = sys.argv[1]
sensors = sys.argv[2]
timestamp = sys.argv[3]
device = sys.argv[4]
location = sys.argv[5]



with open('/app/main/static/img2/pytest.txt', 'w') as f:
        f.write(family + "\n")
        f.write(sensors + "\n")
        f.write(timestamp + "\n")
        f.write(device + "\n")
        f.write(location + "\n")
