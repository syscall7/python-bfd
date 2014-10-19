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


    /** Platform Options Portion **/
    $http.get('/odaweb/api/disassembler/0/architectures/').success(function(data){
        $scope.architectures = data.architectures
        $scope.endians = data.endians
    });

    var updateOptions = function() {
        $http.get('/odaweb/api/disassembler/0/options/?arch=' + $scope.options.architecture).success(function(data){            console.log('OPTIONS', data);
            $scope.options.platformOptions = data.options;
            $.each($scope.options.platformOptions, function(i, po){
                po.selectedValue = null;

                for(var i=0; i<po.values.length; i++) {
                    for (var j=0; j<odbFile.binary.options.selected_opts; j++) {
                        if (po.values[i] == odbFile.binary.options.selected_opts[j]) {
                            po.selectedValue = po.values[i];
                        }
                    }
                }

                if (po.selectedValue == null) {
                    po.selectedValue = 'DEFAULT'
                }
            });
        });
    };

    updateOptions()

    $scope.$watch('options.architecture', function(){
        updateOptions();
    });

});