odaApplication.controller('SectionsController', function SectionsController($scope, $http, $window, odbFile, odaSession) {

    $scope.sections = odbFile.sections;

    var labels = ['label-success', 'label-warning', 'label-important', 'label-info', 'label-inverse'];
    var label_index = 0;
    var flagLabelMap = [];

    $scope.getFlagLabel = function(flag) {
        var label;

        if (flagLabelMap[flag] == undefined) {
            flagLabelMap[flag] = labels[label_index];
            label_index = (label_index+1) % labels.length;
        }

        label = flagLabelMap[flag];

        return label;
    }

    $scope.getFlagText = function(flag) {
        //return flag;
        var s = flag.split('_');
        return s[s.length-1];
    };

    $scope.setPosition = function(position) {
        odaSession.moveToOffset(position);
    }
});

