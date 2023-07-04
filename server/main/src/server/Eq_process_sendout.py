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

# Load Equipment CSV data into memory
csv_data = []
try:
    with open(csv_filename_eq, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_data.append(row)
except FileNotFoundError:
    pass
    # print("File not found")

# Modify the data
for row in csv_data:
    # Check if timestamp, family, and device match and location is empty
    if int(row['timestamp']) == timestamp and row['family'] == family and row['device'] == device and row['location'] == '':
        # Update the location
        row['location'] = location

# Write the modified data back to the CSV file
with open(csv_filename_eq, 'w', newline='') as csvfile:
    fieldnames = ['timestamp', 'family', 'device', 'location', 'key', 'value']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in csv_data:
        writer.writerow(row)

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
    
    location = location[:-1] + 'yd'
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