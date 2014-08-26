odaApplication.controller('StringsController', function StringsController($scope, $http, $window, odbFile, odaSession) {

    $scope.strings = odbFile.strings;

    $scope.setPosition = function(position) {
        console.log('set position', position);
        odaSession.moveToOffset(position);
    }
});