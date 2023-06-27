import sys
import json
import csv
from datetime import datetime, timedelta

family = sys.argv[1]
sensors = sys.argv[2]
timestamp = int(sys.argv[3])
device = sys.argv[4]
location = sys.argv[5]

with open('/app/main/static/img2/eq_process_sendout.txt', 'w') as f:
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

def process_data(location):
    # Extract the bluetooth data
    
    
    return location



location = process_data(location)

# create a dictionary with the location
result = {
    'location': location
}

# Convert the result back to a JSON string
result_json = json.dumps(result)

# Print the JSON string
print(result_json)


with open('/app/main/static/img2/processed_data_sendout.txt', 'a') as f:
        f.write(location + "\n")