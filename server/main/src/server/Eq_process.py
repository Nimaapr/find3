import sys
import json
import sqlite3


family = sys.argv[1]
sensors = sys.argv[2]
timestamp = sys.argv[3]
device = sys.argv[4]
location = sys.argv[5]

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('Eq_beacons.db')
c = conn.cursor()

# Create table (if it doesn't exist)
c.execute('''CREATE TABLE IF NOT EXISTS Eq_beacons 
             (timestamp TEXT, family TEXT, device TEXT, location TEXT, 
              beacon TEXT, value INTEGER)''')

def process_data(data):
    # Extract the bluetooth data
    bluetooth_data = data["bluetooth"]

    # modified_bluetooth = {}
    # for key, value in bluetooth_data.items():
    #     if key.startswith("St"):
    #         modified_bluetooth[key] = value
    #     elif key.startswith("Eq"):
    #         # Insert into SQLite database
    #         c.execute("INSERT INTO Eq_beacons VALUES (?, ?, ?, ?, ?, ?)", 
    #                   (timestamp, family, device, location, key, value))
    #         conn.commit()

    # data["bluetooth"] = modified_bluetooth
    return data

sensor_data = json.loads(sensors)
processed_data = process_data(sensor_data)

# Convert the processed data back to a JSON string
processed_json = json.dumps(processed_data)
print(processed_json)

# Close the connection to the SQLite database
conn.close()








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