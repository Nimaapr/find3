import csv
import json
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import least_squares
import sys
from collections import defaultdict
import logging

logger = logging.getLogger('track')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('track.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - [%(name)s/%(funcName)s] - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)



family = sys.argv[1]
device = sys.argv[2]

logger.debug(f"family data in track: {family}")

with open('/app/main/static/img2/track_data.txt', 'a') as f:
        f.write(device + "\n")
        f.write(family + "\n")

def calculate_distance(rssi, tx_power):
    # tx_power is the RSSI value at 1 meter distance
    # rssi is the RSSI value you measure
    # n is the signal propagation constant (2 for free space, 2-4 for indoor spaces)
    n = 2
    return 10 ** ((tx_power - rssi) / (10 * n))


# Function to perform trilateration
def trilaterate(p1, p2, p3, r1, r2, r3):
    def residuals(p, *params):
        x, y = p
        p1, p2, p3, r1, r2, r3 = params
        return (
            np.sqrt((x - p1[0]) ** 2 + (y - p1[1]) ** 2) - r1,
            np.sqrt((x - p2[0]) ** 2 + (y - p2[1]) ** 2) - r2,
            np.sqrt((x - p3[0]) ** 2 + (y - p3[1]) ** 2) - r3
        )

    result = least_squares(residuals, (0, 0), args=(p1, p2, p3, r1, r2, r3))
    return result.x


def read_data_from_csv(filename):
    data = []
    ref_points = ['0,0', '0,70', '55,190', '450,450', '630, 450', '630, 360', '630, 270', '630, 180']

    with open(filename, 'r') as csvfile:
        # Read the file to get the number of lines
        total_lines = sum(1 for line in csvfile)
        
        # Reset file pointer
        csvfile.seek(0)
        
        # Initialize CSV reader
        reader = csv.DictReader(csvfile)
        
        # Read the file in reverse order
        for current_line, row in enumerate(reversed(list(reader))):
            location = row['location'][2:4]
            row['location'] = ref_points[int(location) - 1]
            
            last_timestamp = float(row['timestamp'])
            if datetime.fromtimestamp(last_timestamp / 1000.0) < datetime.now() - timedelta(minutes=5):
                # We can break as the remaining records are older
                break
            data.append(row)

    # Since we read in reverse, reverse data to preserve time order
    return data[::-1]

# Filter data based on equipment and worker
def filter_data(data, equipment, worker=None):
    return [d for d in data if d['key'].startswith(equipment) and (worker is None or d['device'] == worker)]

# Perform Trilateration on filtered data
def perform_trilateration(filtered_data, tx_power):
    # Group the signals by location
    signals_by_location = defaultdict(list)
    for row in filtered_data:
        location = row['location']
        rssi = float(row['value'])
        signals_by_location[location].append(rssi)
    
    # Average the RSSI values for each location
    avg_rssi_by_location = {loc: sum(rssis) / len(rssis) for loc, rssis in signals_by_location.items()}
    # Select the three locations with the most data
    selected_locations = sorted(avg_rssi_by_location.items(), key=lambda x: len(signals_by_location[x[0]]), reverse=True)[:3]
    if len(selected_locations) < 3:
        return None

    position1 = tuple(map(float, selected_locations[0][0].split(',')))
    position2 = tuple(map(float, selected_locations[1][0].split(',')))
    position3 = tuple(map(float, selected_locations[2][0].split(',')))

    rssi1 = selected_locations[0][1]
    rssi2 = selected_locations[1][1]
    rssi3 = selected_locations[2][1]

    distance1 = calculate_distance(rssi1, tx_power)
    distance2 = calculate_distance(rssi2, tx_power)
    distance3 = calculate_distance(rssi3, tx_power)

    return trilaterate(position1, position2, position3, distance1, distance2, distance3)


# Main function implementing the three approaches
# def main():
csv_filename = '/app/main/static/img2/Eq_beacons.csv'
tx_power = -62  # This should be calibrated for your beacons

equipment = 'Equ'  # Equipment to track
worker = 'worker1'  # Worker to filter by for approach 1

# Step 1: Read data from CSV
data = read_data_from_csv(csv_filename)

# Step 2: Filter data
data_by_worker = filter_data(data, equipment, worker)
data_any_worker = filter_data(data, equipment)

# Step 3: Perform Trilateration
position_by_worker = perform_trilateration(data_by_worker, tx_power)
position_any_worker = perform_trilateration(data_any_worker, tx_power)

# Step 4: Combine approach 1 and 2
if position_by_worker is not None and position_any_worker is not None:
    avg_position = np.mean([position_by_worker, position_any_worker], axis=0)
else:
    avg_position = position_by_worker if position_by_worker is not None else position_any_worker


# Output results
# print(f'Position using data from specific worker: {position_by_worker}')
# print(f'Position using data from any worker: {position_any_worker}')
# print(f'Combined Position: {avg_position}')
# print(avg_position)

# return avg_position


location= avg_position
result = {
'location': location
}

# Convert the result back to a JSON string
result_json = json.dumps(result)

# Print the JSON string
print (result_json)




# ********************************************* test
# create a dictionary with the location
# result = {
#     'location': "location"
# }

# # Convert the result back to a JSON string
# result_json = json.dumps(result)

# # Print the JSON string
# print(result_json)



with open('/app/main/static/img2/Eq_track.txt', 'a') as f:
        f.write(device + "\n")
        f.write(family + "\n")
        f.write(str(result) + "\n")




# def filter_data(device_name):
#     # Get current time
#     current_time = datetime.datetime.now()

#     # Open the CSV file
#     with open('Eq_beacons.csv', 'r') as csvfile:
#         # Read the CSV file
#         reader = csv.DictReader(csvfile)

#         # Process each row
#         for row in reader:
#             # Check if the row matches the device name
#             if row['device'] == device_name:
#                 # Check if the location ends with 'd'
#                 if row['location'].endswith('d'):
#                     # Convert timestamp to datetime
#                     row_time = datetime.datetime.fromtimestamp(int(row['timestamp']) / 1000)

#                     # Check if the time difference is less than 3 minutes and the value is larger than -60
#                     if (current_time - row_time).total_seconds() <= 180 and int(row['value']) > -60:
#                         # This row meets all conditions
#                         print(row)


# # Test the function with a device name
# filter_data(device)
