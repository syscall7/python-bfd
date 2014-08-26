odaApplication.controller('FindBytesController', function FindBytesController($q, $rootScope, $scope, $http, $window, odaStatus) {

    $scope.find = function(bytes)  {
        var deferred = $q.defer();
        odaStatus.setStatus("Searching....");
        var master = oda_util.getMaster();
        odaApi.find(master.short_name, master.revision, bytes).success(function(data){
            odaStatus.setStatus("Done searching");
            $scope.results = data;
            deferred.resolve(data);
        }).error(function(data, status){
            deferred.reject(data);
        });
        return deferred.promise;
    };

    /*
    $scope.FindBytesPrompt = function FindBytesPrompt() {
        var bytes = bootbox.prompt("Bytes to Find:<br>" + $scope.searchHelp,
            function(result) {
                if ((result != null) && (result != "") ) {
                    $rootScope.search_pattern = bytes;
                    find(bytes);
                }
            }
        );
    };
    */

    $scope.setPosition = function(position) {
        //odaApi.setPosition(position);
    };

    $scope.searchHelp = 'To search for ASCII strings, use <b>double quotes</b>, as in:<br>' +
                        '&nbsp;&nbsp;&nbsp;&nbsp;"this is some long string to find"<br><br>' +
                        'To search for a sequnce of hex bytes, use one of the following formats:<br><br>' +
                        '&nbsp;&nbsp;&nbsp;&nbsp;00 01 02 03 de ad be ef<br>' +
                        '&nbsp;&nbsp;&nbsp;&nbsp;00010203deadbeef<br>';

    /*odaApi.shortcut("ctrl f", function() {
        $("#sidebar-find-btn").trigger("click");
        $("#search-pattern").focus();
    }, true); */
});

