odaApplication.controller('LiveEntryController', function SectionsController($scope, $http, $window, odaApi) {

    $scope.liveEntryText = oda_util.getMaster().binary.text;

    var updateText = _.debounce(function() {
        odaApi.setLiveEntryText($scope.liveEntryText);
    }, 500);

    $scope.liveEntryChange = function() {
        updateText();
    };

});