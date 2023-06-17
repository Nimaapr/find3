import sys
import csv
import json
from datetime import datetime, timedelta

family = sys.argv[1]
sensors = sys.argv[2]
device = sys.argv[3]
location = sys.argv[4]




with open('/app/main/static/img2/sendouttest.txt', 'w') as f:
        f.write(family + "\n")
        f.write(sensors + "\n")
        f.write(device + "\n")
        f.write(location + "\n")


# Set CSV filename
csv_filename_wrk = '/app/main/static/img2/Workers_conditions.csv'

# Load worker's last known conditions
workers_conditions = {}
try:
    with open(csv_filename_wrk, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            if timestamp > datetime.now() - timedelta(minutes=2):  # only keep last 2 minutes data
                workers_conditions[row['worker']] = row['condition'], timestamp
except FileNotFoundError:
    pass

# Check worker's last known condition
last_condition, _ = workers_conditions.get(device, (False, datetime.min))

# Print last known condition
print(json.dumps({"device": device, "condition": last_condition}))

# Save worker's conditions
with open(csv_filename_wrk, 'w', newline='') as csvfile:
    fieldnames = ['worker', 'condition', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for worker, (condition, timestamp) in workers_conditions.items():
        writer.writerow({'worker': worker, 'condition': condition, 'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')})