odaApplication.controller('LiveEntryController', function LiveEntryController($scope, $http, $window, odbFile) {

    $scope.oda_master = odbFile.oda_master;

    $scope.liveEntryText = odbFile.binary.text;

    var updateText = _.debounce(function() {
        odbFile.setLiveEntryText($scope.liveEntryText);
        /*.then(function(){
            $scope.entryError = null;
        }).catch(function(ex ){
            $scope.entryError = ex;
        }); */
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

        odbFile.setOptions($scope.options);
    };

});