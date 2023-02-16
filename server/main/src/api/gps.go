package api

/*
This is a Go programming code in the package api. It defines a function GetGPSData which retrieves the latest GPS data based on the input family string.

The function starts by initializing an empty map gpsData of type map[string]models.SensorData. Then it opens a connection to a database (using the function database.Open) with the input family name and a boolean flag that determines whether to open the database in read-only mode.
If there is an error opening the database, the error is wrapped with a custom error message and returned immediately. The database connection is then closed with the defer d.Close() statement.

Next, the code retrieves the locations from the database using the d.GetLocations() method. If there is an error, the error is wrapped with a custom error message and returned immediately.

The code then initializes the gpsData map with default values (latitude = -1, longitude = -1) for each of the retrieved locations.

After that, the code attempts to retrieve the auto GPS data from the database using the d.Get("autoGPS", &autoGPS) method. If the data is successfully retrieved, it updates the values in the gpsData map with the retrieved latitude and longitude values.

Finally, the code attempts to retrieve the custom GPS data from the database using the d.Get("customGPS", &customGPS) method. If the data is successfully retrieved, it updates the values in the gpsData map with the retrieved latitude and longitude values.

The function returns the gpsData map and an error value.
*/

import (
	"github.com/pkg/errors"

	"github.com/Nimaapr/find3/tree/main/server/main/src/database"
	"github.com/Nimaapr/find3/tree/main/server/main/src/models"
)

// GetGPSData returns the latest GPS data
func GetGPSData(family string) (gpsData map[string]models.SensorData, err error) {
	gpsData = make(map[string]models.SensorData)

	d, err := database.Open(family, true)
	if err != nil {
		err = errors.Wrap(err, "You need to add learning data first")
		return
	}
	defer d.Close()

	locations, err := d.GetLocations()
	if err != nil {
		err = errors.Wrap(err, "problem getting locations")
		return
	}

	// initialize
	for _, location := range locations {
		gpsData[location] = models.SensorData{
			GPS: models.GPS{
				Latitude:  -1,
				Longitude: -1,
			},
		}
	}

	// get auto GPS data
	var autoGPS map[string]models.SensorData
	errGet := d.Get("autoGPS", &autoGPS)
	if errGet == nil {
		for location := range autoGPS {
			gpsData[location] = models.SensorData{
				GPS: models.GPS{
					Latitude:  autoGPS[location].GPS.Latitude,
					Longitude: autoGPS[location].GPS.Longitude,
				},
			}
		}
	}

	// get custom GPS data and override gpsdata
	var customGPS map[string]models.SensorData
	errGet = d.Get("customGPS", &customGPS)
	if errGet == nil {
		for location := range customGPS {
			gpsData[location] = models.SensorData{
				GPS: models.GPS{
					Latitude:  customGPS[location].GPS.Latitude,
					Longitude: customGPS[location].GPS.Longitude,
				},
			}
		}
	}

	return
}
