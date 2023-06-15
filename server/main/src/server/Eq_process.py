import sys
import json
import csv
# import sqlite3


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


# Set CSV filename
csv_filename = '/app/main/static/img2/Eq_beacons.csv'

def process_data(data):
    # Extract the bluetooth data
    bluetooth_data = data["bluetooth"]
    
    modified_bluetooth = {}
    for key, value in bluetooth_data.items():
        if key.startswith("St"):
            modified_bluetooth[key] = value
        elif key.startswith("Eq"):
            # Open CSV file and append data
            with open(csv_filename, 'a', newline='') as csvfile:
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




# import sys
# import json

# family = sys.argv[1]
# sensors = sys.argv[2]

# # first extract equipment
# # send back fingerprints
# # equipment data should be saved based on family name
# # save equipment data in CSV with two types: 1) fixed 2) PPE
# # first step: do for PPE

# def process_data(data):
#     # Extract the bluetooth data
#     bluetooth_data = data["bluetooth"]

#     modified_bluetooth = {}
#     for key, value in bluetooth_data.items():
#         if key.startswith("St"):
#             modified_bluetooth[key] = value
#         elif key.startswith("Eq"):
#             # write to a file
#             with open("Eq_beacons.txt", "a") as file:
#                 file.write(f'{key}: {value}\n')

#     data["bluetooth"] = modified_bluetooth
#     return data

# sensor_data = json.loads(sensors)
# processed_data = process_data(sensor_data)

# # Convert the processed data back to a JSON string
# processed_json = json.dumps(processed_data)
# print(processed_json)