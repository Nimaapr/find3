package models

/*
This code defines two Go structs: ByLocationDevice and ByLocation.

The ByLocationDevice struct represents a device and its associated data, including the device name (Device), the device's vendor name (Vendor), a time stamp (Timestamp), a probability score (Probability),
a flag indicating whether or not the data was randomized (Randomized), the number of scanners used to detect the device (NumScanners), the amount of time the device was active (ActiveMins), and the first time the device was seen (FirstSeen).

The ByLocation struct represents a set of devices and their associated data, along with the location they were detected in (Location) and GPS coordinates (GPS). The struct contains an array of ByLocationDevice structs (Devices),
as well as a count of the total number of devices represented in the array (Total).
*/

import "time"

type ByLocationDevice struct {
	Device      string    `json:"device"`
	Vendor      string    `json:"vendor,omitempty"`
	Timestamp   time.Time `json:"timestamp"`
	Probability float64   `json:"probability"`
	Randomized  bool      `json:"randomized"`
	NumScanners int       `json:"num_scanners"`
	ActiveMins  int       `json:"active_mins"`
	FirstSeen   time.Time `json:"first_seen"`
}

type ByLocation struct {
	Devices  []ByLocationDevice `json:"devices"`
	Location string             `json:"location"`
	GPS      GPS                `json:"gps,omitempty"`
	Total    int                `json:"total"`
}
