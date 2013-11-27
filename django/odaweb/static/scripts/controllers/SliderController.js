odaApplication.controller('SliderController', function SliderController($scope, $http, $window, odaApi) {
    var master = oda_util.getMaster();
    var numCodeSections = 0;

    /* sum of all the section address ranges */
    var sumAddrRanges = 0;
    var minAddr = oda_util.getSectionInfo().start_addr;
    var maxAddr = oda_util.getSectionInfo().stop_addr;

    odaApi.getSections(master.short_name, master.revision)
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
        console.log("updateAddrDisplay " + addr.toString(16));
    }

    // event handler for slider control
    $scope.sliderHandler = function (addr) {
        console.log("sliderHandler  " + addr);
        odaApi.setPosition(addr);
    }

    $scope.sliderOptions = {
        change: function( event, ui ) { $scope.updateAddrDisplay(ui.value); },
        slide: function( event, ui ) { $scope.updateAddrDisplay(ui.value); },
        stop: function( event, ui )  { $scope.sliderHandler(ui.value); },
        animate: true,
        min: minAddr,
        max: maxAddr
    };

    $scope.$on('position', function(event, position) {
        $('#slider').slider('value', position);
    });

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
