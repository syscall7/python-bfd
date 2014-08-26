odaApplication.controller('LiveEntryController', function LiveEntryController($scope, $http, $window) {

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

    $scope.options = {
        architecture: $scope.oda_master.binary.options.architecture,
        endian: $scope.oda_master.binary.options.endian,
        base_address: $scope.oda_master.binary.options.base_address
    };

    $scope.optionsUpdated = function() {
        console.log($scope.options);
    };

});