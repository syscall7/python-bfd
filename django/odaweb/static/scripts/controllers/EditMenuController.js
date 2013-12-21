odaApplication.controller('EditMenuController', function EditMenuController($scope, $http, $window, odaApi) {

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

    $("html").keypress(function(event) {
        if (String.fromCharCode(event.which) == 'g' && !commentEditing && !dialogOpen) {
            $scope.GoToAddressPrompt();
        }
        else if (String.fromCharCode(event.which) == ';') {

            if (selectedRow != null) {
                selectedRow.find('.comment').text('   ');
                selectedRow.find('.comment').focus();
            }
        }
    });
});
