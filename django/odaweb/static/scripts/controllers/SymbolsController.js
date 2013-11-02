odaApplication.controller('SymbolsController', function SymbolsController($scope, $http, $window) {
    var master = oda_api.getMaster();

    $http.get('/odaweb/api/symbols/?short_name=' + master.short_name + "&revision=" + master.revision)
        .success(function(data){
            $scope.symbols = data;
        });

    $scope.isDefined = function(symbol) {
        if (symbol.type == 't' || symbol.type == 'T')
            return true;
        else
            return false;

    };
});