odaApplication.controller('LiveEntryController', function SectionsController($scope, $http, $window, odaApi) {

    $scope.liveEntryText = oda_util.getMaster().binary.text;

    $scope.liveEntryChange = function() {
        odaApi.setLiveEntryText($scope.liveEntryText);
    };

});