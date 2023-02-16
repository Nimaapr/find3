package models

/*
The code defines a Go data structure named "ReverseRollingData". This structure contains several fields:

HasData: a boolean field indicating whether the structure has data.
Family: a string field that holds a string value representing the family name.
Datas: an array of SensorData structures, representing the data.
Timestamp: a time.Time field that holds the timestamp for the data.
TimeBlock: a time.Duration field representing the duration of a time block.
MinimumPassive: an integer field representing the minimum passive value.
DeviceLocation: a map field that maps device names to location names.
DeviceGPS: a map field that maps device names to GPS coordinates.
The structure uses the "time" package for the time.Time and time.Duration fields.
*/

import (
	"time"
)

type ReverseRollingData struct {
	HasData        bool
	Family         string
	Datas          []SensorData
	Timestamp      time.Time
	TimeBlock      time.Duration
	MinimumPassive int
	DeviceLocation map[string]string // Device -> Location for learning
	DeviceGPS      map[string]GPS    // Device -> GPS for learning
}
