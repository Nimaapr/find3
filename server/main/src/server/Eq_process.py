import sys
import json
import csv
from datetime import datetime, timedelta

family = sys.argv[1]
sensors = sys.argv[2]
timestamp = sys.argv[3]
device = sys.argv[4]
location = sys.argv[5]

with open('/app/main/static/img2/eq_process.txt', 'w') as f:
        f.write(family + "\n")
        f.write(sensors + "\n")
        f.write(timestamp + "\n")
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
            workers_conditions[row['worker']] = row['condition'], datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
except FileNotFoundError:
    pass

def process_data(data):
    # Extract the bluetooth data
    bluetooth_data = data["bluetooth"]
    
    modified_bluetooth = {}
    for key, value in bluetooth_data.items():
        if key.startswith("St"):
            modified_bluetooth[key] = value
        elif key.startswith("Eq"):
            # Open CSV file and append data
            with open(csv_filename_eq, 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'family', 'device', 'location', 'key', 'value']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # This block writes headers in the CSV file if it was just created
                if csvfile.tell() == 0:
                    writer.writeheader() 

                # Append data to CSV
                writer.writerow({'timestamp': timestamp, 'family': family, 'device': device, 'location': location, 'key': key, 'value': value})

        # Check worker's conditions
        if location.endswith("dd"):
            workers_conditions[device] = (False, timestamp)
        elif location.endswith("d"):
            if key == 'Eq_PPE' and value < -60:
                workers_conditions[device] = (True, timestamp)
            else:
                last_condition, last_timestamp = workers_conditions.get(device, (False, datetime.min))
                if last_condition and last_timestamp > datetime.now() - timedelta(minutes=1):
                    workers_conditions[device] = (True, timestamp)
                else:
                    workers_conditions[device] = (False, timestamp)
        elif location.endswith("s"):
            workers_conditions[device] = (True, timestamp)
        
    data["bluetooth"] = modified_bluetooth
    return data

sensor_data = json.loads(sensors)
processed_data = process_data(sensor_data)

# Save worker's conditions
with open(csv_filename_wrk, 'w', newline='') as csvfile:
    fieldnames = ['worker', 'condition', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for worker, (condition, timestamp) in workers_conditions.items():
        writer.writerow({'worker': worker, 'condition': condition, 'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')})

# Convert the processed data back to a JSON string
processed_json = json.dumps(processed_data)
print(processed_json)

with open('/app/main/static/img2/processed_data.txt', 'w') as f:
        f.write(processed_json + "\n")
