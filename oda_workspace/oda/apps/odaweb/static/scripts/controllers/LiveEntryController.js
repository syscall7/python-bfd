odaApplication.controller('LiveEntryController', function LiveEntryController($scope, $http, $window, odaApi) {

    $scope.oda_master = oda_util.getMaster();

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