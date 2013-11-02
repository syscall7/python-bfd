var odaApplication = angular.module('odaApp',[]).config(function($interpolateProvider) {

});

var oda_api = {
    getMaster : function() { return window.oda_master; }
};



odaApplication.controller('SectionsController', function SectionsController($scope, $http, $window) {
    var master = oda_api.getMaster();

    $http.get('http://localhost:8000/odaweb/api/sections/?short_name=' + master.short_name + " &revision=" + master.revision)
        .success(function(data){
            $scope.sections = data;
        });

    var labels = ['label-success', 'label-warning', 'label-important', 'label-info', 'label-inverse'];
    var label_index = 0;

    $scope.getLabel = function() {

        label_index = (label_index+1) % labels.length;
        var label = labels[ label_index ];
        return label;

    }

    $scope.getFlagText = function(flag) {
        //return flag;
        var s = flag.split('_');
        return s[s.length-1];
    };
});

odaApplication.controller('StringsController', function StringsController($scope, $http, $window) {
    var master = oda_api.getMaster();

    $http.get('http://localhost:8000/odaweb/api/strings/?short_name=' + master.short_name + " &revision=" + master.revision)
        .success(function(data){
            $scope.strings = data;
        });
});

odaApplication.controller('SymbolsController', function SymbolsController($scope, $http, $window) {
    var master = oda_api.getMaster();

    $http.get('http://localhost:8000/odaweb/api/symbols/?short_name=' + master.short_name + " &revision=" + master.revision)
        .success(function(data){
            $scope.symbols = data;
        });

    $scope.isDefined = function(symbol) {
        if (symbol.type == 't' || symbol.type == 'T')
            return true;
        else
            return false;

    };
});

odaApplication.controller('SliderController', function SliderController($scope, $http, $window) {
    var master = oda_api.getMaster();
    var numCodeSections = 0;

    /* sum of all the section address ranges */
    var sumAddrRanges = 0;

    $http.get('http://localhost:8000/odaweb/api/sections/?short_name=' + master.short_name + " &revision=" + master.revision)
        .success(function(data){
            $scope.sections = data;
            sumAddrRanges = _.reduce($scope.sections, function(memo, section) {return memo+section.size}, 0);
        });

    $scope.getSectionWidth = function(section) {
        return (section.size/sumAddrRanges).toString() + '%';
    };

    $scope.getSectionColor = function(section) {
        if (_.contains(_.pluck(section.flags, 'name'), 'SEC_CODE')) {
            return 'blue';
        }
        else{
            return '#303030';
        }
    }
});




