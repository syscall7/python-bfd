var odaApplication = angular
    .module('odaApp',['ngSanitize','ui.keypress'])
    .config(function($interpolateProvider) {

});

var oda_api = {
    getMaster : function() { return window.oda_master; }
};


odaApplication.directive('slider', function ($parse) {
   return {
       restrict: 'A',
       link: function (scope, element, attrs) {
           var options = $parse(attrs.slider)();

           $(element).slider(options);
       }
   };
});

//factory style, more involved but more sophisticated
odaApplication.factory('socketService', function($rootScope) {
    var handler = function (msg) {
        $rootScope.$apply(function () {
          $rootScope.$broadcast("comment", msg);
        });
      };

    socket.on("comment", handler);

    return {

    };
});

odaApplication.factory('odaApi', function($rootScope) {
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
        }
    };
});