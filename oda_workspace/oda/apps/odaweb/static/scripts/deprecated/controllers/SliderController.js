odaApplication.controller('SliderController', function SliderController($scope, $http, $window, odaApi) {
    var master = oda_util.getMaster();

    /* sum of all the section address ranges */
    var sumAddrRanges = 0;
    var minAddr = oda_util.getSectionInfo().start_addr;
    var maxAddr = oda_util.getSectionInfo().stop_addr;

    odaApi.getSections(master.short_name, master.revision)
        .success(function(data){
            $scope.sections = data;
            minAddr = _.min($scope.sections, function(s) {return s.vma}).vma;
            maxAddr = _.max($scope.sections, function(s) {return (s.vma + s.size)}).vma;

            // set initial position
            window.initialOffset = minAddr;
            window.activeTab = "tab-assembly";

            addrBar.setSections($scope.sections);
            $scope.address = minAddr;
        });

    // instantiate the address nav bar
    addrBar = new AddressNavBar('#addr-bar-canvas', $scope.sections);
    addrBar.onChange(function(a) {
        console.log('My change handler: ' + a.toString(16));
        //$scope.$apply(function(){$scope.address = a;});
        odaApi.setPosition(a);
    });
    addrBar.onDrag(function(a) {
        console.log('My drag handler: ' + a.toString(16));
    });

    addrBar.onRoam(function(a) {
        console.log('Roam handler: ' + a.toString(16));
    });

    $scope.$on('position', function(event, position) {
        //TODO This is a hack! Interact with the slider via scope
        if ($scope.address != position) {
            $scope.address=position;

            console.log('Setting slider position to address ' + position.toString(16));
            addrBar.setAddress(position);
        }
    });

    var selectedRow = null;

    $(document).on("click", "#listing tr", function(){
        selectedRow = $(this);
        $('tr.selected').removeClass('selected');
        $(this).addClass('selected');
    });
    $(document).on("hover", "#listing tr", function(){
        //$scope.updateAddrDisplay($(this).attr('addr'));
    });

    odaApi.shortcut(";", function() {
        if (selectedRow != null) {
            selectedRow.find('.comment').text('   ');
            selectedRow.find('.comment').focus();
        }
        console.log("<shortcut> ; pressed");
    });

});
