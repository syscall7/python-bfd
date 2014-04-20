odaApplication.controller('SymbolsController', function SymbolsController($scope, $http, $window, odaApi) {
    var master = oda_util.getMaster();

    odaApi.getSymbols(master.short_name, master.revision)
        .success(function(data){
            $scope.symbols = data;
        });

    $scope.isDefined = function(symbol) {
        if (symbol.type == 't' || symbol.type == 'T')
            return true;
        else
            return false;

    };

    $scope.setPosition = function(position) {
        odaApi.setPosition(position);
    }
});