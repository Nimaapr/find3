package server

import (
	"fmt"
	"net/http"
	"strings"
	"sync"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

// This is a Go code implementing a simple WebSocket server using the Gin Web Framework and Gorilla WebSocket library.
// The purpose of this server is to handle WebSocket connections and send messages to connected clients.
// Let's break down the important parts of this code:

// Import necessary packages.
// Define wsupgrader, an instance of websocket.Upgrader, which helps to upgrade an HTTP connection to a WebSocket connection.
// Define the Websockets struct, which contains a map of WebSocket connections and a Mutex for synchronization.
// Initialize the ws variable of type Websockets and set up the connections map in the init function.
// Implement the wshandler function, which is the main WebSocket handler. It checks for the required query parameters, upgrades the HTTP connection to a
// WebSocket connection, and adds the connection to the map of connections. It also starts two Goroutines: sendOutLocation and websocketListener.
// Implement the websocketListener function, which listens for incoming messages on the WebSocket connection. If there's an error, it removes
// the connection from the map of connections.
// Implement the SendMessageOverWebsockets function, which sends a message to all connected clients for a given family and device. The function iterates over
// the connections map and writes the message to each connection.

// In summary, this code sets up a simple WebSocket server that allows clients to connect and receive messages.
// The server maintains a map of connected clients and can send messages to all clients related to a specific family and device.

var wsupgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

type Websockets struct {
	connections map[string]map[string]*websocket.Conn
	sync.Mutex
}

var (
	ws Websockets
)

func init() {
	ws.Lock()
	defer ws.Unlock()
	ws.connections = make(map[string]map[string]*websocket.Conn)
}

func wshandler(c *gin.Context) {
	family := strings.TrimSpace(c.DefaultQuery("family", ""))
	device := strings.TrimSpace(c.DefaultQuery("device", ""))
	if family == "" {
		c.String(http.StatusBadRequest, "need family")
		return
	} else if device == "" {
		c.String(http.StatusBadRequest, "need device")
		return
	}
	// TODO: validate one-time-pass (otp)
	// otp := c.DefaultQuery("otp", "")
	// if otp == "" {
	// 	return
	// }

	var w http.ResponseWriter = c.Writer
	var r *http.Request = c.Request

	conn, err := wsupgrader.Upgrade(w, r, nil)
	if err != nil {
		fmt.Println("Failed to set websocket upgrade: %+v", err)
		return
	}
	ws.Lock()
	if _, ok := ws.connections[family+"-"+device]; !ok {
		ws.connections[family+"-"+device] = make(map[string]*websocket.Conn)
	}
	ws.connections[family+"-"+device][conn.RemoteAddr().String()] = conn
	ws.Unlock()
	go sendOutLocation(family, device)
	go websocketListener(family, device, conn)
	// Listen to the websockets

}

func websocketListener(family string, device string, conn *websocket.Conn) {
	for {
		_, _, err := conn.ReadMessage()
		if err != nil {
			ws.Lock()
			if _, ok := ws.connections[family+"-"+device]; ok {
				if _, ok2 := ws.connections[family+"-"+device][conn.RemoteAddr().String()]; ok2 {
					delete(ws.connections[family+"-"+device], conn.RemoteAddr().String())
				}
				logger.Log.Debugf("removed %s/%s", family+"-"+device, conn.RemoteAddr().String())
			}
			ws.Unlock()
			return
		}
	}
}

// SendMessageOverWebsockets will send a message over the websockets
func SendMessageOverWebsockets(family string, device string, msg []byte) (err error) {
	ws.Lock()
	defer ws.Unlock()
	if _, ok := ws.connections[family+"-"+device]; ok {
		for _, conn := range ws.connections[family+"-"+device] {
			err = conn.WriteMessage(1, msg)
			if err != nil {
				logger.Log.Warnf("problem sending websocket: %s/%s", family+"-"+device)
			}
		}
	}
	return
}
