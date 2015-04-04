odaApplication.controller('StringsController', function StringsController($scope, $http, $window, odbFile, editor) {

    $scope.strings = odbFile.strings;

    $scope.setPosition = function(position) {
        console.log('set position', position);
        editor.gotoAddress(position);
    }
});