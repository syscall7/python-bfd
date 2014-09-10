var server = require('http').createServer(handler);
var io = require('socket.io').listen(server);
var fs = require('fs');
var bunyan = require('bunyan');

server.listen(8080);

function handler (req, res) {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Request-Method', '*');
    res.setHeader('Access-Control-Allow-Methods', 'OPTIONS, GET');
    res.setHeader('Access-Control-Allow-Headers', '*');

    if ( req.method === 'OPTIONS' ) {
        res.writeHead(200);
        res.end();
        return;
    }

    fs.readFile(__dirname + '/index.html',
    function (err, data) {
        if (err) {
          res.writeHead(500);
          return res.end('Error loading index.html');
        }

        res.writeHead(200);
        res.end(data);
    });
}

var logger = bunyan.createLogger({name: 'socket'});

var numUsers = 0;
var users = {};

function getUsersInRoom(room) {
    //TODO: This will work for small numbers of users, but will blow up
    var foundUsers = [];
    for (var key in users) {
        for (var i=0; i<users[key].length; i++) {
            if (users[key][i].room == room) {
                foundUsers.push(key);
            }
        }
    }
    return foundUsers;
}

io.on('connection', function (socket) {
    logger.info('A New User Has Connected');

    var addedUser = false;
    var currentRoom = null;

    // when the client emits 'add user', this listens and executes
    socket.on('subscribe', function (data) {
        logger.info('subscribe', numUsers, data);

        var username = data.username;
        var room = data.room;

        // we store the username in the socket session for this client
        socket.username = username;
        socket.room = room;

        socket.join(room);


        // add the client's username to the global list
        if (username in users) {
            users[username].push(socket);
        } else {
            users[username] = [socket];
        }
        ++numUsers;

        addedUser = true;
        socket.emit('login', {
            numUsers: numUsers
        });
        // echo data.room that a person has connected

        logger.info("broadcasting join", room, socket.id, socket.rooms);

        socket.to(room).emit('join', {
            username: username,
            numUsers: numUsers
        });

        var usersInRoom = getUsersInRoom(room);
        logger.info('users in room', usersInRoom);
        socket.to(socket.id).emit('users',{
            users: usersInRoom
        });

        currentRoom = room;
    });


    // when the user disconnects.. perform this
    socket.on('disconnect', function () {

    // remove the username from global usernames list
        if (addedUser) {
            var index = users[socket.username].indexOf(socket);
            users[socket.username].splice(index,1);

            //delete users[socket.username];
            --numUsers;
            logger.info(socket.username, ' left ', socket.room, ' leaving ', numUsers);
            // echo globally that this client has left
            socket.broadcast.emit('user left', {
                username: socket.username,
                numUsers: numUsers
            });
        }
    });

    socket.on('cursor.change', function(data){
        logger.info("Cursor Changed", currentRoom, data);
        socket.broadcast.to(currentRoom).emit('cursor.change', data);
    });

    socket.on('comment.create', function(data){
        logger.info("Comment Created", currentRoom, data);
        socket.broadcast.to(currentRoom).emit('comment.create', data);
    });

});

/*
io.sockets.on('connection', function (socket) {

  console.log('A New User Has Connected');
  
  socket.on('subscribe', function(data) { 
    console.log('joined ',data);
    socket.join(data.room);
    socket.broadcast.emit('join', data); 
  });
  
  socket.on('unsubscribe', function(data) {
    console.log('left ' + data.room); 
    socket.leave(data.room); 
  });

  socket.on('comment', function (msg) {
    console.log('I received a comment ', msg);    
    socket.broadcast.emit('comment', msg);
  });
  socket.on('label', function(msg) { 
    console.log('I received a label ',msg);
    socket.broadcast.emit('label', msg);
  });

  socket.on('disconnect', function () {
    io.sockets.emit('user disconnected');
  });



});
*/
