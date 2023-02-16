package api

/*
This code is defining a Go package named api. The package has a global variable named logger which is a pointer to an instance of logging.SeelogWrapper.

The init function initializes the logger by calling the logging.New function and storing the result in the logger variable. If there's an error while initializing the logger, the function panics and terminates the program.

The Debug function is used to control the log level of the logger. If the debugMode argument is true, the logger log level is set to debug using the SetLevel method, otherwise it is set to info.

It's worth noting that this code is using the Seelog logging library, which is an efficient logging library for Go.
*/

import "github.com/Nimaapr/find3/tree/main/server/main/src/logging"

var logger *logging.SeelogWrapper

func init() {
	var err error
	logger, err = logging.New()
	if err != nil {
		panic(err)
	}
	Debug(false)
}

func Debug(debugMode bool) {
	if debugMode {
		logger.SetLevel("debug")
	} else {
		logger.SetLevel("info")
	}
}
