package models

/*
This code is part of a Go package named "models". It defines three structs:

LocationAnalysis:
This struct represents the results of a location analysis. It contains the following fields:

IsUnknown: a boolean flag indicating whether the location is unknown.
LocationNames: a map from location IDs to location names.
Predictions: an array of AlgorithmPrediction structs representing the predictions made by different algorithms.
Guesses: an array of LocationPrediction structs representing the guesses made by the system.


AlgorithmPrediction:
This struct represents the results of a single algorithm's predictions. It contains the following fields:

Locations: an array of location IDs.
Name: the name of the algorithm.
Probabilities: an array of probabilities, one for each location in the "Locations" field.


LocationPrediction:
This struct represents a single prediction of the location. It contains the following fields:

Location: the ID of the location.
Probability: the probability of the prediction.
All three structs are annotated with json:"fieldname" tags, indicating that they can be marshaled and unmarshaled as JSON objects.
*/

type LocationAnalysis struct {
	IsUnknown     bool                  `json:"is_unknown,omitempty"`
	LocationNames map[string]string     `json:"location_names"`
	Predictions   []AlgorithmPrediction `json:"predictions"`
	Guesses       []LocationPrediction  `json:"guesses,omitempty"`
}

type AlgorithmPrediction struct {
	Locations     []string  `json:"locations"`
	Name          string    `json:"name"`
	Probabilities []float64 `json:"probabilities"`
}

type LocationPrediction struct {
	Location    string  `json:"location,omitempty"`
	Probability float64 `json:"probability,omitempty"`
}
