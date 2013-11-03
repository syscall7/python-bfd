var odaApplication = angular.module('odaApp',['ngSanitize']).config(function($interpolateProvider) {

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

