package main

import (
	"flag"
	"log"
	"math/rand"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"runtime"
	"runtime/pprof"
	"strconv"
	"time"

	"fmt"

	"github.com/Nimaapr/find3/server/main/src/api"
	"github.com/Nimaapr/find3/server/main/src/database"
	"github.com/Nimaapr/find3/server/main/src/mqtt"
	"github.com/Nimaapr/find3/server/main/src/server"
)

// 	"math/rand"
// 	"os/exec"
// "strconv"

// This is a Go program that runs a server for a location tracking system called "find3". The program takes in command-line arguments, including ports,
// whether to turn on debugging mode, and whether to use an MQTT server.
// The program then sets up a data folder for the location tracking data and sets up the necessary folders for the system.

// If the user specifies the option to profile memory, the program sets up a routine that profiles memory usage and writes to a file every minute.
// Similarly, if the user specifies the option to profile CPU usage, the program sets up a routine that profiles CPU usage and writes to a file for 30 seconds.

// Finally, the program runs the server and handles any errors that may occur.
// If the user specifies a family database to dump, the program dumps the database, otherwise it runs the server.

func main() {

	go func() {
		for {
			oldName := "/app/main/static/img2/org_floorplan1.png"
			newName := "/app/main/static/org_floorplan2.png"

			erro := os.Rename(oldName, newName)
			if erro != nil {
				panic(erro)
			}

			// Run the Python script every 30 seconds
			time.Sleep(30 * time.Second)
			rand.Seed(time.Now().UnixNano())
			randomInt := rand.Intn(8)
			// is this path to python file correct? maybe use absolute pass?
			cmd := exec.Command("python", "/app/main/src/server/FP_update.py", "1", "test", strconv.Itoa(randomInt))
			var err error
			err = cmd.Run()
			if err != nil {
				log.Println("error running Python script:", err)
			}
		}
	}()

	aiPort := flag.String("ai", "8002", "port for the AI server")
	port := flag.String("port", "8003", "port for the data (this) server")
	debug := flag.Bool("debug", false, "turn on debug mode")
	mqttServer := flag.String("mqtt-server", "", "add MQTT server")
	mqttAdmin := flag.String("mqtt-admin", "admin", "name for mqtt admin")
	mqttPass := flag.String("mqtt-pass", "1234", "password for mqtt admin")
	mqttDir := flag.String("mqtt-dir", "mosquitto_config", "location for mqtt admin")
	dump := flag.String("dump", "", "family database to dump")
	memprofile := flag.Bool("memprofile", false, "whether to profile memory")
	cpuprofile := flag.Bool("cpuprofile", false, "whether to profile cpu")
	var dataFolder string
	flag.StringVar(&dataFolder, "data", "", "location to store data")

	flag.Parse()

	if dataFolder == "" {
		dataFolder, _ = os.Getwd()
		dataFolder = path.Join(dataFolder, "data")
	}
	dataFolder, err := filepath.Abs(dataFolder)
	if err != nil {
		panic(err)
	}
	os.MkdirAll(dataFolder, 0775)

	// setup folders
	database.DataFolder = dataFolder
	api.DataFolder = dataFolder

	// setup debugging
	database.Debug(*debug)
	api.Debug(*debug)
	server.Debug(*debug)
	mqtt.Debug = *debug

	if os.Getenv("MQTT_ADMIN") != "" {
		mqtt.AdminUser = os.Getenv("MQTT_ADMIN")
	} else {
		mqtt.AdminUser = *mqttAdmin
	}
	if os.Getenv("MQTT_PASS") != "" {
		mqtt.AdminPassword = os.Getenv("MQTT_PASS")
	} else {
		mqtt.AdminPassword = *mqttPass
	}
	if os.Getenv("MQTT_SERVER") != "" {
		mqtt.Server = os.Getenv("MQTT_SERVER")
	} else {
		mqtt.Server = *mqttServer
	}
	mqtt.MosquittoConfigDirectory = *mqttDir

	api.AIPort = *aiPort
	api.MainPort = *port
	server.Port = *port
	server.UseMQTT = mqtt.Server != ""

	if *memprofile {
		memprofilePath := path.Join(dataFolder, "memprofile")
		os.MkdirAll(memprofilePath, 0755)
		go func() {
			for {
				time.Sleep(1 * time.Second)
				log.Println("profiling memory")
				f, err := os.Create(path.Join(memprofilePath, fmt.Sprintf("%d.memprofile", time.Now().UnixNano()/int64(time.Millisecond))))
				if err != nil {
					log.Fatal("could not create memory profile: ", err)
				}
				runtime.GC() // get up-to-date statistics
				if err := pprof.WriteHeapProfile(f); err != nil {
					log.Fatal("could not write memory profile: ", err)
				}
				f.Close()
				time.Sleep(60 * time.Second)
			}
		}()
	}

	if *cpuprofile {
		cpuprofilepath := path.Join(dataFolder, "cpuprofile")
		os.MkdirAll(cpuprofilepath, 0755)
		go func() {
			log.Println("profiling cpu")
			f, err := os.Create(path.Join(cpuprofilepath, fmt.Sprintf("%d.cpuprofile", time.Now().UnixNano()/int64(time.Millisecond))))
			if err != nil {
				log.Fatal("could not create cpuprofile profile: ", err)
			}
			err = pprof.StartCPUProfile(f)
			if err != nil {
				log.Fatal("could not create cpuprofile profile: ", err)
			}
			time.Sleep(30 * time.Second)
			pprof.StopCPUProfile()
			log.Println("finished profiling")
		}()
	}
	if *dump != "" {
		err = api.Dump(*dump)
	} else {
		err = server.Run()
	}
	if err != nil {
		fmt.Print("error: ")
		fmt.Println(err)
	}
}
