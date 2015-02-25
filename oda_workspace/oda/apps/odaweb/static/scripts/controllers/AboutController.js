odaApplication.controller('AboutController', function AboutController($scope) {

    var rev = '$LastChangedRevision$'.split(' ')[1];
    $scope.release_version = 'TBD-r' + rev;
    $scope.release_date = '$LastChangedDate$'.split(' ')[1]
});

