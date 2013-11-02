odaApplication.controller('DisassemblyController', function DisassemblyController($scope, $http, $window) {
    var master = oda_api.getMaster();

    $http.get('/odaweb/api/displayunits/?short_name=' + master.short_name + " &revision=" + master.revision)
        .success(function(data){
            $scope.displayUnits = data;
        });
});