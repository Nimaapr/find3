import csv
import json
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import least_squares


family = sys.argv[1]
device = sys.argv[2]

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
    ref_points = ['0,0', '7,1', '9,12', '450,450', '630, 450', '630, 360', '630, 270', '630, 180']

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
            if datetime.fromtimestamp(last_timestamp / 1000.0) < datetime.now() - timedelta(minutes=20):
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
    if len(filtered_data) < 3:
        return None

    position1 = (float(filtered_data[0]['location'].split(",")[0]), float(filtered_data[0]['location'].split(",")[1]))
    position2 = (float(filtered_data[1]['location'].split(",")[0]), float(filtered_data[1]['location'].split(",")[1]))
    position3 = (float(filtered_data[2]['location'].split(",")[0]), float(filtered_data[2]['location'].split(",")[1]))

    rssi1 = float(filtered_data[0]['value'])
    rssi2 = float(filtered_data[1]['value'])
    rssi3 = float(filtered_data[2]['value'])

    distance1 = calculate_distance(rssi1, tx_power)
    distance2 = calculate_distance(rssi2, tx_power)
    distance3 = calculate_distance(rssi3, tx_power)

    return trilaterate(position1, position2, position3, distance1, distance2, distance3)


# Main function implementing the three approaches
# def main():
#     csv_filename = '/app/main/static/img2/Eq_beacons.csv'
# #     csv_filename = './random_data.csv'
#     tx_power = -59  # This should be calibrated for your beacons
    
#     equipment = 'Equ'  # Equipment to track
#     worker = 'worker1'  # Worker to filter by for approach 1
    
#     # Step 1: Read data from CSV
#     data = read_data_from_csv(csv_filename)
    
#     # Step 2: Filter data
#     data_by_worker = filter_data(data, equipment, worker)
#     data_any_worker = filter_data(data, equipment)
    
#     # Step 3: Perform Trilateration
#     position_by_worker = perform_trilateration(data_by_worker, tx_power)
#     position_any_worker = perform_trilateration(data_any_worker, tx_power)
    
#     # Step 4: Combine approach 1 and 2
#     if position_by_worker is not None and position_any_worker is not None:
#         avg_position = np.mean([position_by_worker, position_any_worker], axis=0)
#     else:
#         avg_position = position_by_worker if position_by_worker is not None else position_any_worker

    
#     # Output results
#     # print(f'Position using data from specific worker: {position_by_worker}')
#     # print(f'Position using data from any worker: {position_any_worker}')
#     # print(f'Combined Position: {avg_position}')
#     print(avg_position)


# main()
# result = {
# 'location': str((np.ndarray([1,2])))
# }
# result_json = json.dumps(result)
# print (result_json)




# ********************************************* test
# create a dictionary with the location
result = {
    'location': location
}

# Convert the result back to a JSON string
result_json = json.dumps(result)

# Print the JSON string
print(result_json)



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
