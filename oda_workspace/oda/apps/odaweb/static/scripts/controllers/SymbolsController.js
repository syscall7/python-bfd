"use strict";

odaApplication.controller('SymbolsController', function SymbolsController($scope, $http, $window, odbFile, editor) {

    $scope.symbols = odbFile.symbols;

    $scope.isDefined = function(symbol) {
        if (symbol.type == 't' || symbol.type == 'T')
            return true;
        else
            return false;

    };

    odbFile.on(ODB_EVENTS.CHANGED, function(){
        $scope.$apply();
    });

    $scope.setPosition = function(position) {
        console.log('set position', position);
        editor.gotoAddress(position);
    };
});