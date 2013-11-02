odaApplication.controller('DisassemblyController', function DisassemblyController($scope, $http, $window) {
    var master = oda_api.getMaster();

    var loadDisassembly = function()  {
        $http.get('/odaweb/api/displayunits/?short_name=' + master.short_name + " &revision=" + master.revision)
            .success(function(data){
                $scope.displayUnits = data;
        });
    };

    $http.get('/odaweb/api/comments/?short_name=' + master.short_name + " &revision=" + master.revision)
        .success(function(data) {
            $scope.comments = {};
            $.each(data, function(i,comment){
                $scope.comments[comment.offset] = comment;
            });

            loadDisassembly();
    });

    $scope.getComments = function(offset) {
        return $scope.comments[offset];
    };

});