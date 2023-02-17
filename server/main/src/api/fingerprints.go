package api

/*
The purpose of this code is to save and process sensor data and location predictions in a database.

The code defines two main functions:

SaveSensorData - This function validates and stores sensor data in a database. If the data contains GPS information, it updates that as well.
SavePrediction - This function stores location predictions in the database.
Additionally, there is a helper function "updateCounter", which maintains a count of the number of new fingerprints for each family. If the number of new fingerprints for a particular family exceeds 5, the code will trigger a re-calibration process.

There is also a struct "UpdateCounterMap" which holds the count of locations for each family, and uses a RWMutex to synchronize access to it from multiple goroutines. The globalUpdateCounter variable is an instance of this struct, and the init() function initializes the count map.
*/

import (
	"sync"
	"time"

	"github.com/Nimaapr/find3/server/main/src/database"
	"github.com/Nimaapr/find3/server/main/src/models"
)

type UpdateCounterMap struct {
	// Data maps family -> counts of locations
	Count map[string]int
	sync.RWMutex
}

var globalUpdateCounter UpdateCounterMap

func init() {
	globalUpdateCounter.Lock()
	defer globalUpdateCounter.Unlock()
	globalUpdateCounter.Count = make(map[string]int)
}

// SaveSensorData will add sensor data to the database
func SaveSensorData(p models.SensorData) (err error) {
	err = p.Validate()
	if err != nil {
		return
	}
	db, err := database.Open(p.Family)
	if err != nil {
		return
	}
	err = db.AddSensor(p)
	if p.GPS.Longitude != 0 && p.GPS.Latitude != 0 {
		db.SetGPS(p)
	}
	db.Close()
	if err != nil {
		return
	}

	if p.Location != "" {
		go updateCounter(p.Family)
	}
	return
}

// SavePrediction will add sensor data to the database
func SavePrediction(s models.SensorData, p models.LocationAnalysis) (err error) {
	db, err := database.Open(s.Family)
	if err != nil {
		return
	}
	err = db.AddPrediction(s.Timestamp, p.Guesses)
	db.Close()
	return
}

func updateCounter(family string) {
	globalUpdateCounter.Lock()
	if _, ok := globalUpdateCounter.Count[family]; !ok {
		globalUpdateCounter.Count[family] = 0
	}
	globalUpdateCounter.Count[family]++
	count := globalUpdateCounter.Count[family]
	globalUpdateCounter.Unlock()

	logger.Log.Debugf("'%s' has %d new fingerprints", family, count)
	if count < 5 {
		return
	}
	db, err := database.Open(family)
	if err != nil {
		return
	}
	var lastCalibrationTime time.Time
	err = db.Get("LastCalibrationTime", &lastCalibrationTime)
	defer db.Close()
	if err == nil {
		if time.Since(lastCalibrationTime) < 5*time.Minute {
			return
		}
	}
	logger.Log.Infof("have %d new fingerprints for '%s', re-calibrating since last calibration was %s", count, family, time.Since(lastCalibrationTime))
	globalUpdateCounter.Lock()
	globalUpdateCounter.Count[family] = 0
	globalUpdateCounter.Unlock()

	// debounce the calibration time
	err = db.Set("LastCalibrationTime", time.Now().UTC())
	if err != nil {
		logger.Log.Error(err)
	}

	go Calibrate(family, true)
}
