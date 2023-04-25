import sys
import json

device_num = sys.argv[1]
location_all = json.loads(sys.argv[2])


with open('/app/main/static/img2/kalmanfilter2.txt', 'w') as f:
        f.write(device_num + "\n")
        f.write(location_all + "\n")


# import sys
# import json
# import numpy as np
# from pykalman import KalmanFilter

# def apply_kalman_filter(data):
#     # Extract the bluetooth data
#     bluetooth_data = data["s"]["bluetooth"]

#     # Set up the Kalman filter
#     kf = KalmanFilter(initial_state_mean=-65, n_dim_obs=1)
#     kf.observation_covariance = np.array([[3]])  # Measurement noise covariance matrix (R)
#     kf.transition_covariance = np.array([[0.1]])  # Process noise covariance matrix (Q)

#     # Apply the Kalman filter to the bluetooth data
#     for key, rssi in bluetooth_data.items():
#         measurements = np.array([rssi])
#         filtered_values, _ = kf.filter(measurements)
#         bluetooth_data[key] = float(filtered_values[-1])

#     # Update the data with the filtered bluetooth data
#     data["s"]["bluetooth"] = bluetooth_data

#     return data



# input_json = json.loads(sys.stdin.read())
# filtered_json = apply_kalman_filter(input_json)
# print(json.dumps(filtered_json))
# with open('/app/main/static/img2/kalmanfilter.txt', 'w') as f:
# # f.write(floor_level + "\n")
# f.write(input_json + "\n")
# f.write(filtered_json + "\n")
