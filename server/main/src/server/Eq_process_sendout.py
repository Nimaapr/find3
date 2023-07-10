import sys
import json
import csv
from datetime import datetime, timedelta

family = sys.argv[1]
sensors = sys.argv[2]
# timestamp= int(datetime.now().timestamp() * 1000)
timestamp = int(sys.argv[3])
device = sys.argv[4]
location = sys.argv[5]
location_org = sys.argv[6]

with open('/app/main/static/img2/eq_process_sendout.txt', 'a') as f:
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
eq_ppe_data = []
try:
    with open(csv_filename_eq, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if row contains Eq_PPE beacon, and timestamp, family, and device match
            if row['key'].startswith('Eq_PPE') and int(row['timestamp']) == timestamp and row['family'] == family and row['device'] == device:
                # Add to the Eq_PPE list
                eq_ppe_data.append(row)
            else:
                # Add to the csv_data list for later saving back to the file
                csv_data.append(row)
except FileNotFoundError:
    pass


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


# ********************************************************************
# Load worker's last known conditions
workers_conditions = {}
# try:
#     with open(csv_filename_wrk, 'r') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             workers_conditions[row['worker']] = row['condition'], int(row['timestamp'])
# except FileNotFoundError:
#     pass
# timestamp= int(datetime.now().timestamp() * 1000)

def process_data(data, location):
    # Extract the bluetooth data
    bluetooth_data = data["bluetooth"]
    filtered_bluetooth_data = {k: v for k, v in bluetooth_data.items() if k.startswith("Eq_PPE")}
    if location.endswith("dd"):
        workers_conditions[device] = (False, timestamp)
        location = location[:-1] + 'nd'
        return location
    elif location.endswith("d"):
        for key, value in filtered_bluetooth_data.items():
            if value > -45:
                workers_conditions[device] = (True, timestamp)
                location = location[:-1] + 'yd'
                return location
            
        last_condition, last_timestamp = workers_conditions.get(device, (False, 0))
        if last_condition:
            if datetime.fromtimestamp(last_timestamp/1000.0)> datetime.now() - timedelta(minutes=1):
                workers_conditions[device] = (True, last_timestamp)
                location = location[:-1] + 'yyd'
                return location
        
        workers_conditions[device] = (False, timestamp)
        location = location[:-1] + 'nd'
        return location
    
    # location has not d or dd at the end:
    return location

    # for key, value in bluetooth_data.items():
    #     # Check worker's conditions
    #     if key.startswith("St"):
    #         if location[-2] == 'y' or location[-2] == 'n' or location[-2] == 'd':
    #            continue
    #     if location.endswith("dd"):
    #         workers_conditions[device] = (False, timestamp)
    #         location = location[:-1] + 'nd'
    #     elif location.endswith("d"):
    #         if key.startswith('Eq_PPE') and value > -65:
    #             workers_conditions[device] = (True, timestamp)
    #             location = location[:-1] + 'yd'
    #         else:
    #             last_condition, last_timestamp = workers_conditions.get(device, (False, 0))
    #             # location = location[:-1] + 'nd'
    #             if last_condition: 
    #                 if datetime.fromtimestamp(last_timestamp/1000.0)> datetime.now() - timedelta(minutes=2):
    #                     # Use previous time until it is replaced with new beacon info
    #                     workers_conditions[device] = (True, last_timestamp)
    #                     location = location[:-1] + 'yyd'
    #             else:
    #                 workers_conditions[device] = (False, timestamp)
    #                 location = location[:-1] + 'nd'
    #     elif location.endswith("s"):
    #         workers_conditions[device] = (True, timestamp)
    #     elif location=='':
    #         workers_conditions[device] = (False, timestamp)
    
    # location = location[:-1] + 'yd'
    return location


sensor_data = json.loads(sensors)
# Add the Eq_PPE data to the sensors dictionary
for eq_ppe in eq_ppe_data:
    # Adding Eq_PPE beacon to the 'bluetooth' key of sensors dictionary
    sensor_data["bluetooth"][eq_ppe['key']] = int(eq_ppe['value'])

if location_org=='':
    location_process= location
else:
    location_process=location_org

location = process_data(sensor_data, location_process)

# Save worker's conditions
with open(csv_filename_wrk, 'w', newline='') as csvfile:
    fieldnames = ['worker', 'condition', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for worker, (condition, timestamp) in workers_conditions.items():
        writer.writerow({'worker': worker, 'condition': condition, 'timestamp': timestamp})


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
        f.write(family + "\n")
        f.write(json.dumps(sensor_data) + "\n")
        f.write(str(timestamp) + "\n")
        f.write(str(workers_conditions) + "\n")