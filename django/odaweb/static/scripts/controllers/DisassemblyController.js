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

    var commentsRequest = odaApi.getComments(master.short_name, master.revision);
    var functionsRequest = odaApi.getFunctions(master.short_name, master.revision);
    var labelsRequest = odaApi.getLabels(master.short_name, master.revision);
    $q.all([commentsRequest, functionsRequest, labelsRequest]).then(function(results) {
        $scope.comments = {};
        $scope.functions = {};
        $scope.labels={};

        comments = results[0];
        functions = results[1];
        labels = results[2];

        $.each(comments.data, function(i,comment){
            $scope.comments[comment.offset] = comment;
        });

        $.each(functions.data, function(i,func){
            $scope.functions[func.offset] = func;
        });

        $.each(labels.data, function(i, label){
            $scope.labels[label.offset] = label;
        });

        loadDisassembly();
    });

    $scope.getLabel = function(displayUnit) {
        var label = $scope.labels[displayUnit.offset];

        if (typeof label == 'undefined') {
            return displayUnit.labelName;
        }

        return label.label;

    };

    $scope.getComment = function(offset) {
        var comment = $scope.comments[offset];
        var prefix = ';';
        if (typeof comment == 'undefined') {
            prefix = '';
            comment = '';
        } else {
            comment = comment.comment;
        }

        return prefix+'&nbsp;'+comment;
    };

    $scope.getFunctionRetval = function(offset) {
        func = $scope.functions[offset];
        if (typeof func == 'undefined') {
            retval = 'unknown'
        } else {
            retval = func.retval;
        }
        return retval;
    };

    $scope.getFunctionArgs = function(offset) {
        func = $scope.functions[offset];
        if (typeof func == 'undefined') {
            args = 'unknown'
        } else {
            args = func.args;
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

    $scope.$on('label', function(event,label){
        oda.alert(label.username + ' renamed a lable on <a href="#'+ label.label +'">0x' + label.offset.toString(16) + '</a>');
        $scope.labels[label.offset] = label;
        console.log(label);
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

    $scope.labelEnter = function($event, displayUnit) {
        var label = $($event.target).text();
        $http.post("/odaweb/api/labels/",{
            object_id : oda_util.getMaster().object_id,
            content_type: oda_util.getMaster().content_type,
            label: label,
            offset: displayUnit.offset
        });

        socketService.sendLabel(label, displayUnit.offset);
        $event.preventDefault();
    };

    $scope.commentEnter = function($event, displayUnit) {
        var comment = $($event.target).text()
        $http.post("/odaweb/api/comments/",{
            object_id : oda_util.getMaster().object_id,
            content_type: oda_util.getMaster().content_type,
            comment: comment,
            offset: displayUnit.offset
        });;
        $scope.comments[comment.offset] = {comment: comment.comment, offset: displayUnit.offset};
        socketService.sendComment(comment, displayUnit.offset);
        $event.preventDefault();
    };

});