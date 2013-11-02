odaApplication.controller('StringsController', function StringsController($scope, $http, $window) {
    var master = oda_api.getMaster();

    $http.get('/odaweb/api/strings/?short_name=' + master.short_name + " &revision=" + master.revision)
        .success(function(data){
            $scope.strings = data;
        });
});