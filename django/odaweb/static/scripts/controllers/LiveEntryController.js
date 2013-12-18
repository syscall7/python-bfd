odaApplication.controller('LiveEntryController', function SectionsController($scope, $http, $window, odaApi) {

    $scope.liveEntryText = oda_util.getMaster().binary.text;

    $scope.liveEntryChange = function() {
        $http({
            method: 'PATCH',
            url: '/odaweb/api/binarystrings/'+oda_util.getMaster().binary.id+"/",
            data: {
              binary_string: $scope.liveEntryText.replace(/\s/g, '')
            }
        });
    };

});