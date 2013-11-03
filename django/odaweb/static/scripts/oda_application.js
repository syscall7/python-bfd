var odaApplication = angular.module('odaApp',[]).config(function($interpolateProvider) {

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



