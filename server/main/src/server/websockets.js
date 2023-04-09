$(document).ready(function () {
    // websockets
    url = 'ws://localhost:8003/ws?family=testdb';
    c = new WebSocket(url);

    send = function (data) {
        console.log("Sending: " + data)
        c.send(data)
    }

    c.onmessage = function (msg) {
        console.log(msg.data)
    }

    c.onopen = function () {
        console.log('connected');
    }
});


// a frontend file that establishes the connection and listens for messages from the server