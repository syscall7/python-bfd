var app = require('http').createServer(handler)
  , io = require('socket.io').listen(app)
  , fs = require('fs')

app.listen(8080);

function handler (req, res) {
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
