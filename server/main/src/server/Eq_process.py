import sys
import json
import csv
from datetime import datetime, timedelta

family = sys.argv[1]
sensors = sys.argv[2]
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

def process_data(data):
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
        
    data["bluetooth"] = modified_bluetooth
    return data



sensor_data = json.loads(sensors)
processed_data = process_data(sensor_data)

# Convert the processed data back to a JSON string
processed_json = json.dumps(processed_data)
print(processed_json)


with open('/app/main/static/img2/processed_data.txt', 'w') as f:
        f.write(processed_json + "\n")
        f.write(location + "\n")
