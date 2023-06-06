# read from database
# do PPE: I should know which PPE is the worker wearing, should I just check the distance between the worker and all the PPE beacons?
# save the worker that saved the beacon!
# should have an input: family, and also location of user
# ask GPT: write the first python code, write the type of sensor, write the call function from Go. tell that just want equ with PPE name to check distance.


import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('Eq_beacons.db')
c = conn.cursor()

# Select all records from the Eq_beacons table
c.execute("SELECT * FROM Eq_beacons")

# Fetch all rows from the last executed SELECT statement
rows = c.fetchall()

# Iterate over each row
for row in rows:
    timestamp = row[0]
    family = row[1]
    device = row[2]
    location = row[3]
    beacon = row[4]
    value = row[5]
    
    # Now you can process the data as you need.
    # print(f'Timestamp: {timestamp}, Family: {family}, Device: {device}, Location: {location}, Beacon: {beacon}, Value: {value}')

# Close the connection to the SQLite database
conn.close()
