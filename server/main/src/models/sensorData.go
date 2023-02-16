package models

/*
The code is written in Golang and defines structs, functions, and methods related to storing and validating sensor data. The main structs defined in the code are SensorData, GPS, FINDFingerprint, and Router.

SensorData is the typical data structure for storing sensor data, it contains the following fields:

Timestamp (an int64): a unique identifier, the time in milliseconds
Family (a string): a group of devices
Device (a string): unique within a family
Location (a string): optional, used for classification
Sensors (a map of map of interface{}): contains a map of sensor data
GPS (a struct of type GPS): optional

GPS is a struct containing GPS data, it has the following fields:

Latitude (a float64)
Longitude (a float64)
Altitude (a float64)

FINDFingerprint is the prototypical information from the fingerprinting device, it has the following fields:

Group (a string)
Username (a string)
Location (a string)
Timestamp (an int64)
WifiFingerprint (a slice of type Router)

Router is the router information for each individual mac address, it has two fields:

Mac (a string)
Rssi (an int)

The SensorData struct has a method named Validate that validates that the fingerprint is okay. It checks if the Family, Device, and Timestamp fields are not empty, if the Timestamp is valid, and if the Sensors data is not empty.
If the Timestamp is equal to 0, the method sets it to the current time in UTC in milliseconds.

The FINDFingerprint struct has a method named Convert that converts it into a SensorData struct.
*/

import (
	"errors"
	"strings"
	"time"
)

// SensorData is the typical data structure for storing sensor data.
type SensorData struct {
	// Timestamp is the unique identifier, the time in milliseconds
	Timestamp int64 `json:"t"`
	// Family is a group of devices
	Family string `json:"f"`
	// Device are unique within a family
	Device string `json:"d"`
	// Location is optional, used for classification
	Location string `json:"l,omitempty"`
	// Sensors contains a map of map of sensor data
	Sensors map[string]map[string]interface{} `json:"s"`
	// GPS is optional
	GPS GPS `json:"gps,omitempty"`
}

// GPS contains GPS data
type GPS struct {
	Latitude  float64 `json:"lat,omitempty"`
	Longitude float64 `json:"lon,omitempty"`
	Altitude  float64 `json:"alt,omitempty"`
}

// Validate will validate that the fingerprint is okay
func (d *SensorData) Validate() (err error) {
	d.Family = strings.TrimSpace(strings.ToLower(d.Family))
	d.Device = strings.TrimSpace(strings.ToLower(d.Device))
	d.Location = strings.TrimSpace(strings.ToLower(d.Location))
	if d.Family == "" {
		err = errors.New("family cannot be empty")
	} else if d.Device == "" {
		err = errors.New("device cannot be empty")
	} else if d.Timestamp < 0 {
		err = errors.New("timestamp is not valid")
	}
	if d.Timestamp == 0 {
		d.Timestamp = time.Now().UTC().UnixNano() / int64(time.Millisecond)
	}
	numFingerprints := 0
	for sensorType := range d.Sensors {
		numFingerprints += len(d.Sensors[sensorType])
	}
	if numFingerprints == 0 {
		err = errors.New("sensor data cannot be empty")
	}
	return
}

// FINDFingerprint is the prototypical information from the fingerprinting device
type FINDFingerprint struct {
	Group           string   `json:"group"`
	Username        string   `json:"username"`
	Location        string   `json:"location"`
	Timestamp       int64    `json:"timestamp"`
	WifiFingerprint []Router `json:"wifi-fingerprint"`
}

// Router is the router information for each invdividual mac address
type Router struct {
	Mac  string `json:"mac"`
	Rssi int    `json:"rssi"`
}

// Convert will convert a FINDFingerprint into the new type of data,
// for backwards compatibility with FIND.
func (f FINDFingerprint) Convert() (d SensorData) {
	d = SensorData{
		Timestamp: int64(f.Timestamp),
		Family:    f.Group,
		Device:    f.Username,
		Location:  f.Location,
		Sensors:   make(map[string]map[string]interface{}),
	}
	if len(f.WifiFingerprint) > 0 {
		d.Sensors["wifi"] = make(map[string]interface{})
		for _, fingerprint := range f.WifiFingerprint {
			d.Sensors["wifi"][fingerprint.Mac] = float64(fingerprint.Rssi)
		}
	}
	return
}
