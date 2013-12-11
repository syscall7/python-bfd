odaApplication.controller('HexController', function HexController($q, $scope, $http, $location, $anchorScroll,
                                                                                  $window, $sanitize, socketService, odaApi, odaStatus) {

    function mouseoverBytes(e) {
        var currentId = e.target.id;
        var addr = currentId.substring(1, currentId.length);
        var ascii = $("#a"+addr);
        var hex = $("#h"+addr);

        ascii.addClass("hex-hovered");
        hex.addClass("hex-hovered");

        var asciiVal = ascii.text().trim();
        // if we trimmed everything away, it must be a SPACE
        if (asciiVal == "")
            asciiVal = " ";

        var status = "Address: <b>" + addr + "h</b> Byte: <b>" + hex.text().trim() + "h</b> ASCII: <b>'" + asciiVal + "'</b>";
        $scope.$apply(function(){odaStatus.setStatus(status);});

        addr = addr.substring(0, addr.length-1) + "0";
        $("#p"+addr).addClass("hex-hovered");
    }

    function mouseoutBytes(e) {
        var currentId = e.target.id;
        var addr = currentId.substring(1, currentId.length);
        $("#a"+addr).removeClass( "hex-hovered");
        $("#h"+addr).removeClass( "hex-hovered");

        addr = addr.substring(0, addr.length-1) + "0";
        $("#p"+addr).removeClass("hex-hovered");
        $scope.$apply(function(){odaStatus.setStatus("");});
    };


    $(".hex-cell-asc").live("mouseover", mouseoverBytes);
    $(".hex-cell-asc").live("mouseout", mouseoutBytes);
    $(".hex-cell-byte").live("mouseover", mouseoverBytes);
    $(".hex-cell-byte").live("mouseout", mouseoutBytes);

    var master = oda_util.getMaster();
    var minAddress = -1;
    var maxAddress = -1

    function convertDisplayUnitsToHexLines(dus)
    {
        var WIDTH = 16;

        $scope.hexLines = [];

        for (var i = 0; i < dus.length; i++) {

            var du = dus[i];
            // add the raw bytes and ascii representation
            for (var b = 0; b < du.rawBytes.length; b+=2) {

                if ((du.offset+b)%WIDTH == 0) {
                    $scope.hexLines.push({
                        name : du.section_name,
                        addr : du.offset,
                        bytes : [],
                        asc : []
                    });
                }

                var index = $scope.hexLines.length - 1;
                byte = du.rawBytes.substring(b,b+2);
                asc = parseInt(byte, 16);
                asc = asc < 32 || asc > 127 ? '.' : String.fromCharCode(asc);
                $scope.hexLines[index].bytes.push(byte);
                $scope.hexLines[index].asc.push(asc);
            }
        }

        // pad out last line to WIDTH
        while ($scope.hexLines[$scope.hexLines.length-1].bytes.length < WIDTH) {
            $scope.hexLines[$scope.hexLines.length-1].bytes.push('  ');
            $scope.hexLines[$scope.hexLines.length-1].asc.push('  ');
        }
    };

    function loadHex (addr)  {
        var deferred = $q.defer();
        odaApi.getDisplayUnits(master.short_name, master.revision, addr).success(function(data){
            displayUnits = data;
            convertDisplayUnitsToHexLines(displayUnits);
            minAddress = displayUnits[0].offset;
            maxAddress = displayUnits[displayUnits.length-1].offset;
            console.log("minAddress:"+ minAddress + " maxAddress:"+maxAddress);
            deferred.resolve(data);
        }).error(function(data, status){
            deferred.reject(data);
        });
        return deferred.promise;
    };

    loadHex();

    $scope.$on('position', function(event, position) {
        console.log('position changed' + position);

        var handleScroll = function() {
            //$location.hash("addr-" + $scope.location);
            // call $anchorScroll()
            //$anchorScroll();
        };

        if (position < minAddress || position > maxAddress) {
            //oda.alert("reloading...");
            loadHex(position).then(function(data){
                if (position < minAddress || position > maxAddress) {
                    //if we still are out of position, then we're in trouble
                    oda.alert("We're not in position");
                } else {
                    $scope.location = position;
                    handleScroll();
                }
            });
        } else {
            $scope.location = position;
            handleScroll();
        }
    });


});