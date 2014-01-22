odaApplication.controller('LiveEntryController', function SectionsController($scope, $http, $window, odaApi) {

    $scope.liveEntryText = oda_util.getMaster().binary.text;

    var updateText = _.debounce(function() {
        odaApi.setLiveEntryText($scope.liveEntryText).then(function(){
            $scope.entryError = null;
        }).catch(function(ex ){
            $scope.entryError = ex;
        });
    }, 1000);

    $scope.liveEntryChange = function() {
        updateText();
    };

});