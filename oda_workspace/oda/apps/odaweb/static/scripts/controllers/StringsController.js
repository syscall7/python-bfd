odaApplication.controller('StringsController', function StringsController($scope, $http, $window, odaApi, OdaSession) {
    var master = oda_util.getMaster();

    odaApi.getStrings(master.short_name, master.revision).success(function(data){
        $scope.strings = data;
    } );

    $scope.setPosition = function(position) {
        console.log('set position', position);
        OdaSession.getSession().moveToOffset(position);
    }
});