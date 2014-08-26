odaApplication.controller('SymbolsController', function SymbolsController($scope, $http, $window, odbFile, OdaSession) {

    $scope.symbols = odbFile.symbols;

    $scope.isDefined = function(symbol) {
        if (symbol.type == 't' || symbol.type == 'T')
            return true;
        else
            return false;

    };

    $scope.setPosition = function(position) {
        console.log('set position', position);
        OdaSession.getSession().moveToOffset(position);
    };
});