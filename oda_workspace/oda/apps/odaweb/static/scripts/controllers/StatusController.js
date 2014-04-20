odaApplication.controller('StatusController', function SliderController($scope, $http, $window, odaStatus) {
    $scope.status = odaStatus.getStatus();
    $scope.oda_master = window.oda_master;
    $scope.binary = window.oda_master.binary;
});