import os
import operator
import hashlib
import sys
import random

import requests
import randomcolor
import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
from scipy.stats import gaussian_kde
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# This code is a Python script that fetches data from a specified URL, processes the data to extract sensor data for each location, 
# identifies the sensors with the largest variance in the data, and generates plots of the sensor data for each location.

# Here is a high-level overview of what the script does:
# Sends a GET request to the specified URL and extracts the data from the response in JSON format.

# Processes the JSON data to extract sensor data for each location, and calculates the median value of each sensor's data across all locations.

# Calculates the variance of each sensor across all locations, and identifies the sensors with the largest variance (up to a maximum of 10 sensors).

# Generates plots of the sensor data for each location using the identified sensors, with the x-axis representing the range of sensor data values and the y-axis representing the density of data values within that range. 
# The plots are saved as PNG images in a specified directory.

# The colors for the plotted sensor data are generated randomly using the randomcolor library, with each sensor being assigned a unique color.










def getcolor(s):
    random.seed(int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**8)
    return randomcolor.RandomColor().generate()[0]

def plot_data(url,path_to_data):
    r = requests.get(url)
    if 'data' not in r.json():
        raise Exception("problem getting url")

    locationSensors = {}
    for d in r.json()['data']:
        if 'l' not in d or d['l'] == '':
            continue
        loc = d['l']
        if loc not in locationSensors:
            locationSensors[loc] = {}
        for s in d['s']:
            for mac in d['s'][s]:
                sensorName = s+'-'+mac
                if sensorName not in locationSensors[loc]:
                    locationSensors[loc][sensorName] = []
                locationSensors[loc][sensorName].append(d['s'][s][mac])

    # find largest variance
    sensorIndex = []
    locationIndex = []
    for location in locationSensors:
        locationIndex.append(location)
        for sensorID in locationSensors[location]:
            if sensorID not in sensorIndex:
                sensorIndex.append(sensorID)
    num_locations = len(locationIndex)
    num_sensors = len(sensorIndex)
    X = numpy.zeros([len(sensorIndex),len(locationSensors)])

    for i,location in enumerate(locationIndex):
        for j,sensorID in enumerate(sensorIndex):
            if sensorID not in locationSensors[location]:
                continue
            X[j,i] = numpy.median((locationSensors[location][sensorID]))


    varianceOfSensorID = {}
    for i,row in enumerate(X):
        data = []
        for v in row:
            if v == 0:
                continue
            data.append(v)
        varianceOfSensorID[sensorIndex[i]] = numpy.var(data)

    # collect sensor ids that are most meaningful
    sensorIDs = []
    for i, data in enumerate(
            sorted(varianceOfSensorID.items(), key=operator.itemgetter(1),reverse=True)):
        if data[1] == 0:
            continue
        sensorIDs.append(data[0])
        if len(sensorIDs) == 10:
            break


    bins = numpy.linspace(-100, 0, 100)
    for location in locationSensors:
        pyplot.figure(figsize=(10,4))

        for sensorID in sensorIDs:
            if sensorID not in locationSensors[location]:
                continue
            try:
                density = gaussian_kde(locationSensors[location][sensorID])
            except Exception as e:
                continue
            density.covariance_factor = lambda : .5
            density._compute_covariance()
            pyplot.fill(bins,density(bins),alpha=0.2,label=sensorID,facecolor=getcolor(sensorID))
            # pyplot.hist(
            #     locationSensors[location][sensorID],
            #     bins,
            #     alpha=0.5,
            #     label=sensorID)
            if i == 10:
                break
        pyplot.title(location)
        pyplot.legend(loc='upper right')
        pyplot.savefig(os.path.join(path_to_data,location + ".png"))
        pyplot.close()
