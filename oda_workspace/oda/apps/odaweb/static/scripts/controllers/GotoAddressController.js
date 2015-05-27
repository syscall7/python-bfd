odaApplication.controller('GotoAddressController', function($scope, $modalInstance, editor) {

    $scope.data = {
        address: null
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function () {
        var position = parseInt($scope.data.address.substring(2),16);
        console.log('set position', position);
        editor.gotoAddress(position);
        $modalInstance.close({address: $scope.data.address});
    };

});