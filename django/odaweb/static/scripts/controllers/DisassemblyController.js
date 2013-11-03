odaApplication.controller('DisassemblyController', function DisassemblyController($q, $scope, $http, $window, $sanitize, socketService, odaApi) {
    var master = oda_util.getMaster();

    var minAddress = -1;
    var maxAddress = -1

    var loadDisassembly = function(addr)  {
        var deferred = $q.defer();
        $http.get('/odaweb/api/displayunits/?', {
            params: {
                short_name : master.short_name,
                revision : master.revision,
                addr : addr
            }
        }).success(function(data){
            $scope.displayUnits = data;
            minAddress = $scope.displayUnits[0].offset;
            maxAddress = $scope.displayUnits[$scope.displayUnits.length-1].offset;
            console.log("minAddress:"+ minAddress + " maxAddress:"+maxAddress);
            deferred.resolve(data);
        }).error(function(data, status){
            deferred.reject(data);
        });
        return deferred.promise;
    };

    odaApi.getComments(master.short_name, master.revision)
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
        oda.alert(comment.username + " commented on 0x" + comment.offset.toString(16));
        $scope.comments[comment.offset] = {comment: comment.comment, offset: comment.offset};
        console.log($scope.comments);
    });

    $scope.$on('position', function(event, position) {
        console.log('position changed' + position);
        if (position < minAddress || position > maxAddress) {
            console.log("outside window, need to reload");
            loadDisassembly(position).then(function(data){
                if (position < minAddress || position > maxAddress) {
                    //if we still are out of position, then we're in trouble
                    oda.alert("We're not in position");
                } else {
                    alert('scroll');
                }
            });
        }

    })


    $scope.commentEnter = function($event, displayUnit) {
        var comment = $($event.target).text()
        $.post("/odaweb/comment", { comment: comment, offset: displayUnit.offset } );
        $scope.comments[comment.offset] = {comment: comment.comment, offset: displayUnit.offset};
        socketService.sendComment(comment, displayUnit.offset);
        $event.preventDefault();
    };

});