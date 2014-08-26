odaApplication.controller('StringsController', function StringsController($scope, $http, $window, odbFile, OdaSession) {

    $scope.strings = odbFile.strings;

    $scope.setPosition = function(position) {
        console.log('set position', position);
        OdaSession.getSession().moveToOffset(position);
    }
});