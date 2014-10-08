$(document).ready(function(){

    var master = oda_util.getMaster();
    socket.emit('subscribe', {
        username : window.user.username,
        room : master.short_name
    });

    socket.on('join', function(data) {
        console.log('join', data);
        oda.alert('User ' + data.username + ' has joined this session');
    });

    /*socket.on('comment', function (data) {
        oda.alert('comment');
    });*/

});