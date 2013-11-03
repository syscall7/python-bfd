odaApplication.controller('SectionsController', function SectionsController($scope, $http, $window) {
    var master = oda_util.getMaster();

    $http.get('/odaweb/api/sections/?short_name=' + master.short_name + "&revision=" + master.revision)
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

