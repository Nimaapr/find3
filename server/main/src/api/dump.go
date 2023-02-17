package api

/*
This code defines a Go package named api that contains two functions, Dump and writeDatas. The Dump function exports data from a database for a given family of data.
The writeDatas function takes the family name, a string name and an array of SensorData, and writes the data to a file in JSON format.

The Dump function opens a connection to the database for the given family using the database.Open function, and retrieves all the data for classification using db.GetAllForClassification and all the data not for classification using db.GetAllNotForClassification.
If there is no data to dump, the function returns an error message. If there is data to dump, the function calls the writeDatas function to write the data to a file in JSON format.
The filename is constructed using a combination of the family name, the name string and the timestamp of the last data item. Before writing, the function removes any existing file with the same name, and uses the json package to marshal each data item into its JSON representation.
After writing, the function calls f.Sync to flush the data to disk.
*/

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"

	"github.com/Nimaapr/find3/server/main/src/models"

	"github.com/Nimaapr/find3/server/main/src/database"
)

func Dump(family string) (err error) {
	defer logger.Log.Flush()
	// gather the data
	db, err := database.Open(family, true)
	if err != nil {
		return
	}
	defer db.Close()
	datasLearn, err := db.GetAllForClassification()
	if err != nil {
		return
	}
	datasTrack, err := db.GetAllNotForClassification()
	if err != nil {
		return
	}

	if len(datasLearn) == 0 && len(datasTrack) == 0 {
		err = errors.New("no data to dump for " + family)
	}
	if len(datasLearn) > 0 {
		err = writeDatas(family, "learn", datasLearn)
		if err != nil {
			return
		}
	}
	if len(datasTrack) > 0 {
		err = writeDatas(family, "track", datasTrack)
		if err != nil {
			return
		}

	}

	return
}

func writeDatas(family string, name string, datas []models.SensorData) (err error) {
	fname := fmt.Sprintf("%s.%s.%d.jsons", family, name, datas[len(datas)-1].Timestamp)
	os.Remove(fname)
	f, err := os.Create(fname)
	if err != nil {
		return
	}
	defer f.Close()
	for _, data := range datas {
		bData, errMarshal := json.Marshal(data)
		if errMarshal != nil {
			return errMarshal
		}
		f.Write(bData)
		f.Write([]byte("\n"))
	}
	f.Sync()
	logger.Log.Infof("dumped data to %s", fname)
	return
}
