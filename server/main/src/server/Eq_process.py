import sys
import json
import csv
from datetime import datetime, timedelta

family = sys.argv[1]
sensors = sys.argv[2]
# timestamp = sys.argv[3]
# timestamp = datetime.datetime.fromtimestamp(int(timestamp) / 1000)
# timestamp = datetime.fromtimestamp(int(sys.argv[3]))
timestamp = int(sys.argv[3])
device = sys.argv[4]
location = sys.argv[5]

with open('/app/main/static/img2/eq_process.txt', 'w') as f:
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
    for key, value in bluetooth_data.items():
        if key.startswith("St"):
            modified_bluetooth[key] = value
        elif key.startswith("Equ"):
            # convert the elif from "Equ" to "Eq" to save all the equipment
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
            # with open('/app/main/static/img2/processed_data.txt', 'a') as f:
            #     f.write("inside the location d condition" + "\n")
            if key.startswith('Eq_PPE') and value > -65:
                workers_conditions[device] = (True, timestamp)
                location = location[:-1] + 'yd'
                # with open('/app/main/static/img2/processed_data.txt', 'a') as f:
                #     f.write("inside the Eq_PPE condition " + str(workers_conditions)+device+ "\n")
            else:
                last_condition, last_timestamp = workers_conditions.get(device, (False, 0))
                if last_condition and datetime.fromtimestamp(last_timestamp/1000.0)> datetime.now() - timedelta(minutes=1):
                    # Use previous time until it is replaced with new beacon info
                    workers_conditions[device] = (True, last_timestamp)
                    location = location[:-1] + 'yd'
                else:
                    workers_conditions[device] = (False, timestamp)
                    location = location[:-1] + 'nd'
        elif location.endswith("s"):
            workers_conditions[device] = (True, timestamp)
        
    data["bluetooth"] = modified_bluetooth
    return data, location



sensor_data = json.loads(sensors)
processed_data, location = process_data(sensor_data, location)

# with open('/app/main/static/img2/processed_data.txt', 'a') as f:
#         f.write("after running the function "+str(workers_conditions) + "\n")

# Save worker's conditions
with open(csv_filename_wrk, 'w', newline='') as csvfile:
    fieldnames = ['worker', 'condition', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for worker, (condition, timestamp) in workers_conditions.items():
        writer.writerow({'worker': worker, 'condition': condition, 'timestamp': timestamp})

# Convert the processed data back to a JSON string
processed_json = json.dumps(processed_data)
print(processed_json)

# # uncomment if you want to return location and sensor data
# # Combine processed_data and location into a single dictionary
# result = {
#     'location': location,
#     'data': processed_data
# }
# # Convert the result back to a JSON string
# result_json = json.dumps(result)

# # Print the JSON string
# print(result_json)

with open('/app/main/static/img2/processed_data.txt', 'a') as f:
        f.write(processed_json + "\n")
        f.write(location + "\n")
