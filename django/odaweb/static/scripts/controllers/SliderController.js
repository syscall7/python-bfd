odaApplication.controller('SliderController', function SliderController($scope, $http, $window, odaApi) {
    var master = oda_util.getMaster();
    var numCodeSections = 0;

    /* sum of all the section address ranges */
    var sumAddrRanges = 0;
    var minAddr = oda_util.getSectionInfo().start_addr;
    var maxAddr = oda_util.getSectionInfo().stop_addr;

    $scope.address = 0;
    var mapSliderpointToAddress = function(x) {
        var sum = 0;
        var i = 0;
        for(; i<$scope.sections.length; i++) {
            sum += $scope.sections[i].size;
            if (sum>x) break;
        }
        //var percentInSection = ((x-sum) + $scope.sections[i].size) / $scope.sections[i].size
        var addr = ((x-sum) + $scope.sections[i].size) + $scope.sections[i].vma;
        return addr;
    };

    var mapAddressToSliderpoint = function(addr) {
        var i=0;
        var size=0;
        for(; i<$scope.sections.length; i++) {
            size+=$scope.sections[i].size;
            if ($scope.sections[i].vma>addr) break;
        }
        var x= (size-$scope.sections[i-1].size) + (addr -$scope.sections[i-1].vma);
        return x;
    };

    odaApi.getSections(master.short_name, master.revision)
        .success(function(data){
            $scope.sections = data;
            sumAddrRanges = _.reduce($scope.sections, function(memo, section) {return memo+section.size}, 0);

            $scope.sliderOptions.max = sumAddrRanges;

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
        //console.log("updateAddrDisplay " + addr.toString(16));
    }

    // event handler for slider control
    $scope.sliderHandler = function (x) {
        console.log("sliderHandler  " + x);
        var addr = mapSliderpointToAddress(x);
        odaApi.setPosition(addr);
        $scope.$apply(function(){$scope.address = addr;});
    }

    $scope.sliderOptions = {
        change: function( event, ui ) { $scope.updateAddrDisplay(ui.value); },
        slide: function( event, ui ) { $scope.updateAddrDisplay(ui.value); },
        stop: function( event, ui )  { $scope.sliderHandler(ui.value); },
        animate: true,
        min: 0,
        max: 100
    };

    $scope.$on('position', function(event, position) {
        //TODO This is a hack! Interact with the slider via scope
        $scope.address=position;
        $('#slider').slider('value', mapAddressToSliderpoint(position));
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
});
