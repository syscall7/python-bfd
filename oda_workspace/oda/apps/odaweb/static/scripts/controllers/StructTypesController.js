odaApplication.controller('StructTypesController', function StructTypesController($scope, $http, $window, odbFile, odaSession) {

    $scope.structTypes = odbFile.structTypes;

});