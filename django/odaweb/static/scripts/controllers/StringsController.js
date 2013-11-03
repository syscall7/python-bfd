odaApplication.controller('StringsController', function StringsController($scope, $http, $window, odaApi) {
    var master = oda_util.getMaster();

    odaApi.getStrings(master.short_name, master.revision).success(function(data){
        $scope.strings = data;
    } );

    $scope.setPosition = function(position) {
        odaApi.setPosition(position);
    }
});