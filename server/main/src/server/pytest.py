import sys
import json
import numpy as np
# from pykalman import KalmanFilter
import json

sensors = sys.argv[1]



with open('/app/main/static/img2/pytest.txt', 'w') as f:
        f.write(sensors + "\n")
