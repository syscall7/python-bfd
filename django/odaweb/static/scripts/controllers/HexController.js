odaApplication.controller('HexController', function HexController($q, $scope, $http, $location, $anchorScroll,
                                                                                  $window, $sanitize, socketService, odaApi) {

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
        $("#status-bar-left").html(status);

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
        $("#status-bar-left").html("");
    };


    $(".hex-cell-asc").live("mouseover", mouseoverBytes);
    $(".hex-cell-asc").live("mouseout", mouseoutBytes);
    $(".hex-cell-byte").live("mouseover", mouseoverBytes);
    $(".hex-cell-byte").live("mouseout", mouseoutBytes);


    /* TODO: Construct this from the displayUnits data we already have access to on the client */
    $scope.hexLines = [
        {
            name : '.text',
            addr : 0x12345678,
            bytes : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            asc : ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a']
        },
        {
            name : '.text',
            addr : 0x55555555,
            bytes : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            asc : ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a']
        }

    ]

});