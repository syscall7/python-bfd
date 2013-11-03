odaApplication.controller('DisassemblyController', function DisassemblyController($q, $scope, $http, $location, $anchorScroll,
                                                                                  $window, $sanitize, socketService, odaApi) {
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

    var commentsReq = odaApi.getComments(master.short_name, master.revision);
    var prototypesReq = odaApi.getPrototypes(master.short_name, master.revision);
    $q.all([commentsReq, prototypesReq]).then(function(results) {
        $scope.comments = {};
        $scope.prototypes = {};
        comments = results[0];
        prototypes = results[1];
        $.each(comments, function(i,comment){
            $scope.comments[comment.offset] = comment;
        });

        $.each(prototypes, function(i,prototype){
            $scope.prototypes[prototype.offset] = prototype;
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

    $scope.getPrototypeRetval = function(offset) {
        prototype = $scope.prototypes[offset];
        if (typeof prototype == 'undefined') {
            retval = 'unknown'
        } else {
            retval = prototype.retval;
        }
        return retval;
    };

    $scope.getPrototypeArgs = function(offset) {
        prototype = $scope.prototypes[offset];
        if (typeof prototype == 'undefined') {
            args = 'unknown'
        } else {
            args = prototype.args;
        }
        return args;
    };

    $scope.isFunction = function(displayUnit) {
        return displayUnit.isFunction;
    };

    $scope.isLabel = function(displayUnit) {
        return displayUnit.isBranch;
    };

    $scope.isLabeled = function(displayUnit) {
        return displayUnit.isFunction || displayUnit.isBranch;
    };

    $scope.$on('comment', function(event,comment){
        oda.alert(comment.username + ' commented on <a href="#'+ comment.offset +'">0x' + comment.offset.toString(16) + '</a>');
        $scope.comments[comment.offset] = {comment: comment.comment, offset: comment.offset};
        console.log($scope.comments);
    });

    $scope.setPosition = function(position) {
        odaApi.setPosition(position);
    }

    $scope.$on('position', function(event, position) {
        console.log('position changed' + position);

        var handleScroll = function() {
            $location.hash("addr-" + $scope.location);
            // call $anchorScroll()
            $anchorScroll();
        };

        if (position < minAddress || position > maxAddress) {
            oda.alert("reloading...");
            loadDisassembly(position).then(function(data){
                if (position < minAddress || position > maxAddress) {
                    //if we still are out of position, then we're in trouble
                    oda.alert("We're not in position");
                } else {
                    $scope.location = position;
                    handleScroll();
                }
            });
        } else {
            $scope.location = position;
            handleScroll();
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