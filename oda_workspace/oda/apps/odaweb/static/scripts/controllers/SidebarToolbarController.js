odaApplication.controller('SidebarToolbarController', function SectionsController($scope, $http, $window, odaApi) {
    $scope.oda_master = oda_util.getMaster();
});
