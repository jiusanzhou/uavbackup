// Setup basic express server
var express = require('express');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io')(server);
var port = process.env.PORT || 3000;

// var dgram = require('dgram');
// var udpServer =  dgram.createSocket('udp4');
// var udpHost = "127.0.0.1";
// var udpPort = 33333;


// var commands = [];
// var commands_heart = '*';
// var last_command_time = 0;


/*
* TCP server for commands heartbeat
* Send back the commands
*/


/*
* Start a UDP server waitting the log data
*/

// udpServer.on('listening', function () {
//     var address = udpServer.address();
//     console.log('UDP Server listening on ' + address.address + ":" + address.port);
// });

// udpServer.on('message', function (message, remote) {
//     // console.log(remote.address + ':' + remote.port +' - ' + message);
//     msg = message.toString();
//     //console.log(msg);
//     // msg==commands_heart
//     if (msg[0] === '{') {
//       //console.log(msg);
//       io.sockets.emit('update status', {
//         message: msg//.slice(1)
//       });
//     } else {
//       _msg = msg.split('^');
//       io.sockets.emit('log message', {
//         username: _msg[1],
//         message: _msg[0]
//       })
//     };
//     _l = commands.length;      
//     if (_l != 0) {
//       for (var i = 0; i < _l; i++) {
//         // console.log(i);
//         //udpServer.
//         var _m = commands.pop(0);
//         console.log(Date.now());
//         udpServer.send(_m, 0, _m.length, remote.port, remote.address);
//       };
//     } else{
//       udpServer.send(commands_heart, 0, commands_heart.length, remote.port, remote.address)
//     };
// });

// udpServer.bind(udpPort, udpHost);



/*
* Create the socket for client
* Send the log from master
* Get the user's commands or buttun signnel
*/

server.listen(port, function () {
  console.log('Server listening at port %d', port);
});

// Routing
app.use(express.static(__dirname + '/public'));

// Chatroom

// usernames which are currently connected to the chat
var usernames = {};
var numUsers = 0;

var aircraftnames = {};
var aircraftcount = 0;


var STREAM_SECRET = '';
var STREAM_PORT = 2009;// process.argv[3] || 8082,
var WEBSOCKET_PORT = 3001;//process.argv[4] || 8084,
var STREAM_MAGIC_BYTES = 'jsmp'; // Must be 4 bytes
var width = 640;
var height = 480;
var name = 'aircraft';

io.on('connection', function (socket) {
  var addedUser = false;

  socket.on('message', function(data){
    console.log(data);
  });


  /**
  * Events from aircraft
  */

  socket.on('log message', function(data){

    _msg = data.split('^');
    socket.broadcast.emit('log message', {
      username: _msg[1],
      message: _msg[0]
    })
  })

  // when aircraft emits 'update status'
  socket.on('update status', function(data){
    // emit to clients
    // console.log(data.toString());
    socket.broadcast.emit('update status', {
      message: data
    });
  });

  // when aircraft connect
  socket.on('aircraft connected', function(aircraftname){
    console.log(aircraftname);
    socket.aircraftname = aircraftname;
    aircraftnames[aircraftname] = aircraftname;
    ++aircraftcount;
    socket.broadcast.emit('new aircraft', {
      aircraftname: aircraftname,
      aircraftcount: aircraftcount
    })
  })

  socket.on('aircraft disconnect', function (aircraftname) {
    // remove the username from global usernames list
    delete aircraftnames[aircraftname];
    --aircraftcount;

    // echo globally that this client has left
    socket.broadcast.emit('aircraft disconnect', {
      aircraftname: aircraftname,
      aircraftcount: aircraftcount
    });
  });








  // when the client emits 'new message', this listens and executes
  socket.on('new command', function (data) {
    // we tell the aircraft to execute 'new command'
    socket.broadcast.emit('new command', data);
    // if (socket.username == 'amdin') {
    //   var t = Date.now();
    //   if (t - last_command_time > 2000) {
    //     socket.broadcast.emit('new command', data);
    //     last_command_time = t;
    //   }else{
    //     console.log(t - last_command_time);
    //   };
    // };
    //console.log(socket.username + commands.length);
  });

  // when the client emits 'add user', this listens and executes
  socket.on('add user', function (username) {
    // we store the username in the socket session for this client
    socket.username = username;
    // add the client's username to the global list
    usernames[username] = username;
    ++numUsers;
    addedUser = true;
    socket.emit('login', {
      numUsers: numUsers
    });
    // echo globally (all clients) that a person has connected
    socket.broadcast.emit('user joined', {
      username: socket.username,
      numUsers: numUsers
    });
  });

  // when the client emits 'typing', we broadcast it to others
  socket.on('typing', function () {
    socket.broadcast.emit('typing', {
      username: socket.username
    });
  });

  // when the client emits 'stop typing', we broadcast it to others
  socket.on('stop typing', function () {
    socket.broadcast.emit('stop typing', {
      username: socket.username
    });
  });

  // when the user disconnects.. perform this
  socket.on('disconnect', function () {
    // remove the username from global usernames list
    if (addedUser) {
      delete usernames[socket.username];
      --numUsers;

      // echo globally that this client has left
      socket.broadcast.emit('user left', {
        username: socket.username,
        numUsers: numUsers
      });
    }
  });

  // when request video live
  socket.on('stream camera', function(data){
    console.log(data);
    var width = data.width||640;
    var height = data.height||480;
    var name = data.name||'aircraft';
    STREAM_SECRET = name;

    socket.broadcast.emit('start camera stream', {
      name: name,
      width: width,
      height: height
    })
  });

  socket.on('stop camera', function(data){
    socket.broadcast.emit('stop camera stream');
    // socketServer.stop();
    // streamServer.stop()
  });

});


/**
* Server for stream
*/



// Websocket Server
var socketServer = new (require('ws').Server)({port: WEBSOCKET_PORT});
socketServer.on('connection', function(socket) {
    // Send magic bytes and video size to the newly connected socket
    // struct { char magic[4]; unsigned short width, height;}
    var streamHeader = new Buffer(8);
    streamHeader.write(STREAM_MAGIC_BYTES);
    streamHeader.writeUInt16BE(width, 4);
    streamHeader.writeUInt16BE(height, 6);
    socket.send(streamHeader, {binary:true});

    console.log( 'New WebSocket Connection ('+socketServer.clients.length+' total)' );
    
    socket.on('close', function(code, message){
        console.log( 'Disconnected WebSocket ('+socketServer.clients.length+' total)' );
    });
});

socketServer.broadcast = function(data, opts) {
    for( var i in this.clients ) {
        if (this.clients[i].readyState == 1) {
            this.clients[i].send(data, opts);
        }
        else {
            console.log( 'Error: Client ('+i+') not connected.' );
        }
    }
};
console.log('Awaiting WebSocket connections on ws://127.0.0.1:'+WEBSOCKET_PORT);

// HTTP Server to accept incomming MPEG Stream
// var streamServer = require('http').createServer( function(request, response) {
//     var params = request.url.substr(1).split('/');

//     if( params[0] == STREAM_SECRET ) {
//         width = (params[1] || 640)|0;
//         height = (params[2] || 480)|0;
        
//         console.log(
//             'Stream Connected: ' + request.socket.remoteAddress + 
//             ':' + request.socket.remotePort + ' size: ' + width + 'x' + height
//         );
//         request.on('data', function(data){
//             socketServer.broadcast(data, {binary:true});
//         });
//     } else {
//         console.log(
//             'Failed Stream Connection: '+ request.socket.remoteAddress + 
//             request.socket.remotePort + ' - wrong secret.'
//         );
//         response.end();
//     }
// }).listen(STREAM_PORT);


/*
* Start a UDP server live stream
*/
var dgram = require('dgram');
var udpServer =  dgram.createSocket('udp4');
var udpHost = "127.0.0.1";
var udpPort = 2009;

udpServer.on('listening', function () {
    var address = udpServer.address();
    console.log('UDP Server listening on ' + address.address + ":" + address.port);
});

udpServer.on('message', function(data){
  socketServer.broadcast(data, {binary:true});
});

udpServer.bind(udpPort, udpHost);
// udpServer.on('message', function (message, remote) {
//     // console.log(remote.address + ':' + remote.port +' - ' + message);
//     msg = message.toString();
//     //console.log(msg);
//     // msg==commands_heart
//     if (msg[0] === '{') {
//       //console.log(msg);
//       io.sockets.emit('update status', {
//         message: msg//.slice(1)
//       });
//     } else {
//       _msg = msg.split('^');
//       io.sockets.emit('log message', {
//         username: _msg[1],
//         message: _msg[0]
//       })
//     };
//     _l = commands.length;      
//     if (_l != 0) {
//       for (var i = 0; i < _l; i++) {
//         // console.log(i);
//         //udpServer.
//         var _m = commands.pop(0);
//         console.log(Date.now());
//         udpServer.send(_m, 0, _m.length, remote.port, remote.address);
//       };
//     } else{
//       udpServer.send(commands_heart, 0, commands_heart.length, remote.port, remote.address)
//     };
// });

// console.log('Listening for MPEG Stream on http://127.0.0.1:'+STREAM_PORT);//+'/'+name+'/'+width+'/'+height);