odaApplication.controller('OptionsViewController', function SectionsController($scope, $http, $window, odaApi) {

    var arch = oda_util.getMaster().binary.arch;
    $scope.optionsTemplate = function() {
        var view = '/odaweb/optionsview?arch=' + arch
        return view;
    };

    $scope.$on('platformOptionsChanged', function(event, options){
        console.log(options);
        arch = options.arch.trim();
    });
});
