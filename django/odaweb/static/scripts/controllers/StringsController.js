odaApplication.controller('StringsController', function StringsController($scope, $http, $window, odaApi) {
    var master = oda_util.getMaster();

    odaApi.getStrings(master.short_name, master.revision).success(function(data){
        $scope.strings = data;
    } );
    /*$http.get('/odaweb/api/strings/?short_name=' + master.short_name + "&revision=" + master.revision)
        .success(function(data){
            $scope.strings = data;
        });*/
});