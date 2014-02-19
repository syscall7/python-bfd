odaApplication.controller('EditMenuController', function EditMenuController($q, $rootScope, $scope, $http, $window, odaApi, odaStatus) {

    $scope.GoToAddressPrompt = function GoToAddressPrompt() {

        var addr;

        var min = oda_util.getSectionInfo().start_addr;
        var max = oda_util.getSectionInfo().stop_addr;

        // continue prompting until they get it right or give up
        do {

            var strAddr = prompt("Go to address:");

            // if Cancel was not hit and the user actually entered something
            if (strAddr) {

                // prepend '0x'
                if (strAddr.substring(0,2) != '0x')
                    strAddr = '0x' + strAddr;

                addr = Number(strAddr);
                // must be a number
                if (isNaN(addr)) {
                    oda.alert('Address must be hexadecimal in the form of "AABB..." or "0xAABB..."');
                    continue;
                }
                // must be within range
                else if ((addr < min) || (addr > max)) {
                    addr = NaN;
                    oda.alert('Address must be in the range 0x' + min.toString(16) + ' to  0x' + max.toString(16));
                    continue;
                }

            }
            // else, Cancel was clicked
            else {
                return;
            }
        } while (isNaN(addr));

        odaApi.setPosition(addr);
    }

    $scope.find = function(bytes)  {
        var deferred = $q.defer();
        odaStatus.setStatus("Searching....");
        var master = oda_util.getMaster();
        odaApi.find(master.short_name, master.revision, bytes).success(function(data){
            odaStatus.setStatus("Done searching");
            $rootScope.results = data;
            deferred.resolve(data);
        }).error(function(data, status){
            deferred.reject(data);
        });
        return deferred.promise;
    };

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

    $scope.setPosition = function(position) {
        odaApi.setPosition(position);
    };

    $scope.searchHelp = 'To search for ASCII strings, use <b>double quotes</b>, as in:<br>' +
                        '&nbsp;&nbsp;&nbsp;&nbsp;"this is some long string to find"<br><br>' +
                        'To search for a sequnce of hex bytes, use one of the following formats:<br><br>' +
                        '&nbsp;&nbsp;&nbsp;&nbsp;00 01 02 03 de ad be ef<br>' +
                        '&nbsp;&nbsp;&nbsp;&nbsp;00010203deadbeef<br>';

    // TODO: Where should this listener go?
    var listener = new window.keypress.Listener();

    listener.simple_combo("ctrl g", function() {
        $scope.GoToAddressPrompt();
    }, true);

    listener.simple_combo("ctrl f", function() {
        $("#sidebar-find-btn").trigger("click");
        $("#search-pattern").focus();
    }, true);



    $("html").keypress(function(event) {
        if (String.fromCharCode(event.which) == ';') {

            if (selectedRow != null) {
                selectedRow.find('.comment').text('   ');
                selectedRow.find('.comment').focus();
            }
        }
    });
});
