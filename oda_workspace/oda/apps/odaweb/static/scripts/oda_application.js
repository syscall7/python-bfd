$.fn.exists = function () {
    return this.length !== 0;
}

var odaApplication = angular
    .module('odaApp',['ngSanitize','ui.keypress','ui.event'])
    .config(function($httpProvider) {

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

});

var oda_util = {
    getMaster : function() { return window.oda_master; },
    getUsername: function() { return window.user.username},
    getSectionInfo: function() { return window.oda_master.section_info;}

};

/* Bill: Why can't I put this here?

        oda_shortcuts = new window.keypress.Listener();

   I get "Cannot read property 'addEventListener' of null".  If I assign it later, everything is fine.
 */
var oda_shortcuts = null;

//factory style, more involved but more sophisticated
odaApplication.factory('socketService', function($rootScope) {
    var createHandler = function (messageType) {
        var handler = function (msg) {
            $rootScope.$apply(function () {
                $rootScope.$broadcast(messageType, msg);
            });
        };
        return handler;
    };

    socket.on("comment", createHandler('comment'));
    socket.on("label", createHandler('label'));

    return {
        sendComment : function(comment, offset) {
            socket.emit('comment', {
                username: oda_util.getUsername(),
                comment: comment,
                offset: offset
            });
        },
        sendLabel : function(label, offset) {
            socket.emit('label', {
                username: oda_util.getUsername(),
                label: label,
                offset: offset
            });
        }
    };
});

odaApplication.factory('odaStatus', function($rootScope, $q, $http) {
    var status= {
        text: 'Loaded'
    };
    return {
        getStatus : function() {
            return status;
        },
        setStatus : function(newStatus) {
            status.text = newStatus;
        }

    };
});

odaApplication.factory('odaApi', function($rootScope, $q, $http) {

    var position = 0;

    return {
        getStrings : function(short_name, revision) {
            var deferred = $q.defer();
            return $http.get('/odaweb/api/strings/?short_name=' + short_name + "&revision=" + revision)
                .success(function(data, status) {
                // Some extra manipulation on data if you want...
                deferred.resolve(data);
            }).error(function(data, status) {
                deferred.reject(data);
            });

            return deferred.promise;
        },
        getSections : function(short_name, revision) {
            return $http.get('/odaweb/api/sections/', {
                params: {
                    short_name : short_name,
                    revision : revision
                },
                cache: true
            });
        },
        getDisplayUnits : function(short_name, revision, addr, quantity) {
            return $http.get('/odaweb/api/displayunits/?', {
                params: {
                    short_name : short_name,
                    revision : revision,
                    addr : addr,
                    units : quantity
                }/*,
                cache: true*/
            });
        },
        getSymbols : function(short_name, revision) {
            return $http.get('/odaweb/api/symbols/?short_name=' + short_name + "&revision=" + revision);
        },
        getComments : function(short_name, revision) {
            return $http.get('/odaweb/api/comments/?short_name=' + short_name + "&revision=" + revision);
        },
        getFunctions : function(short_name, revision) {
            console.debug('getting functions for ' + short_name + ' revision ' + revision);
            return $http.get('/odaweb/api/functions/', {
                params: {
                    short_name : short_name,
                    revision : revision
                }
            });
        },
        setLabel : function(id, label) {
            return $http({
                method: 'PATCH',
                url: '/odaweb/api/labels/'+id+"/",
                data: {
                  label: label
                }
            });
        },
        setOdaOptions: function(id, target, arch) {
            return $http({
                method: 'PATCH',
                url: '/odaweb/api/odaoptions/'+id+"/",
                data: {
                  target: target,
                  architecture: arch
                }
            });
        },
        setComment : function(id, comment) {
            return $http({
                method: 'PATCH',
                url: '/odaweb/api/comments/'+id+"/",
                data: {
                  comment: comment
                }
            });
        },
        getLabels : function(short_name, revision) {
            return $http.get('/odaweb/api/labels/', {
                params: {
                    short_name : short_name,
                    revision : revision
                }
            });
        },
        getPosition: function() {
            return postion;
        },
        setPosition: function(newPosition) {
            if (position != newPosition) {
                console.log("setting new position to " + newPosition.toString(16));
                position = newPosition;
                $rootScope.$broadcast("position", position);
            }
        },
        setLiveEntryText: function(liveEntryText) {
            var deferred = $q.defer();

            $http({
                method: 'PATCH',
                url: '/odaweb/api/binarystrings/'+oda_util.getMaster().binary.id+"/",
                data: {
                  binary_string: liveEntryText.replace(/\s/g, ''),
                  short_name: oda_util.getMaster().short_name,
                  revision: oda_util.getMaster().revision
                }
            }).success(function(data){
                $rootScope.$broadcast("liveEntryText", position);
                deferred.resolve(data);
            }).error(function(){
                deferred.reject("Use only hex characters!");
            });
            return deferred.promise;
        },
        updatePlatformOptions: function(options) {
             $rootScope.$broadcast("liveEntryText", position);
             $rootScope.$broadcast("platformOptionsChanged", options);
        },
        find : function(short_name, revision, bytes) {
            return $http.get('/odaweb/api/find/?short_name=' + short_name + "&revision=" + revision + "&bytes=" + bytes);
        },
        shortcut : function(combo, func) {
            if (oda_shortcuts == null)
            {
                oda_shortcuts = new window.keypress.Listener();
            }
            oda_shortcuts.simple_combo(combo, func, true);
        }
    };
});

odaApplication.filter('hex', function () {
        return function (num, len) {
            var numStr = num.toString(16);
            len = parseInt(len, 10);
            if (isNaN(num) || isNaN(len)) {
                return n;
            }
            numStr = ''+numStr;
            while (numStr.length < len) {
                numStr = '0'+numStr;
            }
            return numStr;
        };
    });