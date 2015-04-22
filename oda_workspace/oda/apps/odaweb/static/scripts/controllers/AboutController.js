odaApplication.controller('AboutController', function AboutController($scope) {

    var rev = '$LastChangedRevision$'.split(' ')[1];
    $scope.release_version = '0.3.0' + rev;
    $scope.release_date = '$LastChangedDate$'.split(' ')[1]
});

