# read from database
# do PPE: I should know which PPE is the worker wearing, should I just check the distance between the worker and all the PPE beacons?
# save the worker that saved the beacon!
# should have an input: family, and also location of user
# ask GPT: write the first python code, write the type of sensor, write the call function from Go. tell that just want equ with PPE name to check distance.


import csv
import datetime


family = sys.argv[1]
sensors = sys.argv[2]
device = sys.argv[4]
location = sys.argv[5]



def filter_data(device_name):
    # Get current time
    current_time = datetime.datetime.now()

    # Open the CSV file
    with open('Eq_beacons.csv', 'r') as csvfile:
        # Read the CSV file
        reader = csv.DictReader(csvfile)

        # Process each row
        for row in reader:
            # Check if the row matches the device name
            if row['device'] == device_name:
                # Check if the location ends with 'd'
                if row['location'].endswith('d'):
                    # Convert timestamp to datetime
                    row_time = datetime.datetime.fromtimestamp(int(row['timestamp']) / 1000)

                    # Check if the time difference is less than 3 minutes and the value is larger than -60
                    if (current_time - row_time).total_seconds() <= 180 and int(row['value']) > -60:
                        # This row meets all conditions
                        print(row)


# Test the function with a device name
filter_data(device)
