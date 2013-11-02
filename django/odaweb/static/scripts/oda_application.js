var odaApplication = angular.module('odaApp',[]).config(function($interpolateProvider) {

});

var oda_api = {
    getMaster : function() { return window.oda_master; }
};

odaApplication.controller('SliderController', function SliderController($scope, $http, $window) {
    var master = oda_api.getMaster();
    var numCodeSections = 0;

    /* sum of all the section address ranges */
    var sumAddrRanges = 0;
    var minAddr = 0;
    var maxAddr = 0xFFFFFFFF;

    $http.get('http://localhost:8000/odaweb/api/sections/?short_name=' + master.short_name + " &revision=" + master.revision)
        .success(function(data){
            $scope.sections = data;
            sumAddrRanges = _.reduce($scope.sections, function(memo, section) {return memo+section.size}, 0);

            minAddr = _.min($scope.sections, function(s) {return s.vma});
            maxAddr = _.max($scope.sections, function(s) {return s.vma});

            // set initial position
            window.initialOffset = minAddr;
            window.activeTab = "tab-assembly";
            $scope.updateAddrDisplay($("#slider").slider("value"));

        });

    $scope.getSectionWidth = function(section) {
        return (section.size/sumAddrRanges).toString() + '%';
    };

    $scope.getSectionColor = function(section) {
        if (_.contains(_.pluck(section.flags, 'name'), 'SEC_CODE')) {
            return 'blue';
        }
        else{
            return '#303030';
        }
    };

    // set the slider address display text
    // NOTE: This function is triggered via updateSlider() in history.js as well
    $scope.updateAddrDisplay = function (addr) {
        window.topDisplayAddr = addr;
        addrStr = addr.toString(16).toUpperCase();
        while (addrStr.length < 8) addrStr = "0" + addrStr;
        $("#slider-address").text("0x" + addrStr);
    }

    // event handler for slider control
    $scope.sliderHandler = function (addr) {

        alert(addr);
        debugger;

        // no need to set the slider position, that's already been done by the event
        $scope.updateAddrDisplay(addr);

        // Try to scroll to the address
        if ( !scrollToAddr(addr) )
        {
            // Isn't loaded. Try to load it
            //window.topDisplayAddr = addr;
            updateDisplayedFileContent(addr,false);
            scrollToAddr(addr);
        }
    }

    $scope.sliderOptions = {
        change: function( event, ui ) { $scope.updateAddrDisplay(ui.value); },
        slide: function( event, ui ) { $scope.updateAddrDisplay(ui.value); },
        stop: function( event, ui )  { $scope.sliderHandler(ui.value); },
        animate: true,
        min: minAddr,
        max: maxAddr
    };

    var selectedRow = null;

    // remove border
    $(".ui-slider-horizontal").css('border', 0);
    $(".ui-slider-handle").removeClass('ui-corner-all');

    $(document).on("click", "#listing tr", function(){
        selectedRow = $(this);
        $('tr.selected').removeClass('selected');
        $(this).addClass('selected');
    });
    $(document).on("hover", "#listing tr", function(){
        $scope.updateAddrDisplay($(this).attr('addr'));
    });

    $("html").keypress(function(event) {
        if (String.fromCharCode(event.which) == 'g' && !commentEditing && !dialogOpen) {
            GoToAddressPrompt();
        }
        else if (String.fromCharCode(event.which) == ';') {

            if (selectedRow != null) {
                selectedRow.find('.comment').text('   ');
                selectedRow.find('.comment').focus();
            }
        }
    });
});

odaApplication.directive('slider', function ($parse) {
   return {
       restrict: 'A',
       link: function (scope, element, attrs) {
           var options = $parse(attrs.slider)();

           $(element).slider(options);
       }
   };
});



