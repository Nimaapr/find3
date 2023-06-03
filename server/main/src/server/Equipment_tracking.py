import sys
import json
import numpy as np
import json

family = sys.argv[1]
sensors = sys.argv[2]

# first extract equipment
# send back fingerprints
# save equipment data in CSV with two types: 1) fixed 2) PPE
# first step: do for PPE

def process_data(data):
    # Extract the bluetooth data
    bluetooth_data = data["bluetooth"]
    # process later

    return data

sensor_data = json.loads(sensors)
station_data = process_data(sensor_data)
# Convert the filtered data back to a JSON string
station_data_jason = json.dumps(station_data)
print(station_data_jason)