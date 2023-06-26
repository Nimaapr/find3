import sys
import json
import csv
from datetime import datetime, timedelta

family = sys.argv[1]
sensors = sys.argv[2]
timestamp = int(sys.argv[3])
device = sys.argv[4]
location = sys.argv[5]

with open('/app/main/static/img2/eq_process_sendout.txt', 'a') as f:
        f.write(family + "\n")
        f.write(sensors + "\n")
        f.write(str(timestamp) + "\n")
        f.write(device + "\n")
        f.write(location + "\n")

# Set CSV filenames
csv_filename_eq = '/app/main/static/img2/Eq_beacons.csv'
csv_filename_wrk = '/app/main/static/img2/Workers_conditions.csv'

# Load worker's last known conditions
workers_conditions = {}
try:
    with open(csv_filename_wrk, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            workers_conditions[row['worker']] = row['condition'], int(row['timestamp'])
except FileNotFoundError:
    pass

def process_data(data, location):
    # Extract the bluetooth data
    bluetooth_data = data["bluetooth"]
    
    modified_bluetooth = {}
    modified_bluetooth = bluetooth_data
        
    data["bluetooth"] = modified_bluetooth
    return data, location



sensor_data = json.loads(sensors)
processed_data, location = process_data(sensor_data, location)

# Convert the processed data back to a JSON string
processed_json = json.dumps(processed_data)

# Combine processed_data and location into a single dictionary
result = {
    'location': location,
    'data': processed_data
}

# Convert the result back to a JSON string
result_json = json.dumps(result)

# Print the JSON string
print(result_json)

# print(processed_json)
