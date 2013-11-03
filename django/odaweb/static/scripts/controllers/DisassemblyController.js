odaApplication.controller('DisassemblyController', function DisassemblyController($scope, $http, $window, $sanitize) {
    var master = oda_api.getMaster();

    var loadDisassembly = function()  {
        $http.get('/odaweb/api/displayunits/?short_name=' + master.short_name + "&revision=" + master.revision)
            .success(function(data){
                $scope.displayUnits = data;
        });
    };

    $http.get('/odaweb/api/comments/?short_name=' + master.short_name + "&revision=" + master.revision)
        .success(function(data) {
            $scope.comments = {};
            $.each(data, function(i,comment){
                $scope.comments[comment.offset] = comment;
            });

            loadDisassembly();
    });

    $scope.getComment = function(offset) {
        comment = $scope.comments[offset];
        prefix = ';';
        if (typeof comment == 'undefined') {
            prefix = '';
            comment = '';
        } else {
            comment = comment.comment;
        }

        return prefix+'&nbsp;'+comment;
    };

    $scope.isFunction = function(displayUnit) {
        var p = displayUnit.instStr.indexOf("push") !== -1;
        return false;
    };

    $scope.isLabel = function(displayUnit) {
        return false;
    };

    $scope.isLabeled = function(displayUnit) {
        return false;
    };

    $scope.$on('comment', function(event,comment){
        oda.alert('comment');
        $scope.comments[comment.offset] = {comment: comment.comment, offset: comment.offset};
        console.log($scope.comments);
    });

    $scope.commentEnter = function($event, displayUnit) {
        var comment = $($event.target).text()
        $.post("/odaweb/comment", { comment: comment, offset: displayUnit.offset } );
        $event.preventDefault();
    };

});