//Socket IO
odaApplication.run(function($rootScope, addrBar, odbFile, odaSession){
    var socket = io.connect("http://" + window.location.hostname + ":8080", {
        reconnection: false
    });

    socket.on('connect', function(){
        console.log('connected');

        socket.on('join', function(data) {
            console.log('join', data);
            addrBar.addUser(data.username);
            addrBar.updateUser(data.username, 0x403000);
            $rootScope.$broadcast('user.connect', data.username);
        });

        socket.on('cursor.change', function(e){
            addrBar.updateUser(e.username, e.offset);
        });

        odaSession.on('cursor.change', function(e){
            var currentUser = $rootScope.currentUser;
            socket.emit('cursor.change',{
                username: currentUser.username,
                offset: e.offset
            });
        });

        var currentUser = $rootScope.currentUser;
        socket.emit('subscribe',{
            //todo username
            username: currentUser.username,
            room: odbFile.shortName
        });

        socket.on('user.left', function(e) {
            console.log('leave', e);
            $rootScope.$broadcast('user.disconnect', e.username)
        });


        socket.on('users', function(e) {
            console.log('users', e);
            for (var i=0;i< e.users.length; i++ ) {
                $rootScope.$broadcast('user.connect', e.users[i]);
            }
        });

        socket.on('user.error', function(e) {
            toastr.error("Connection Error: " + e.error);
        })

    });

});