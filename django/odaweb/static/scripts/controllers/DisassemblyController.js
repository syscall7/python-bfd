odaApplication.controller('DisassemblyController', function DisassemblyController($q, $scope, $http, $location, $anchorScroll,
                                                                                  $window, $sanitize, socketService, odaApi, odaStatus) {
    var master = oda_util.getMaster();

    var minAddress = -1;
    var maxAddress = -1

    var loadDisassembly = function(addr)  {
        var deferred = $q.defer();
        odaApi.getDisplayUnits(master.short_name, master.revision, addr).success(function(data){
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

    var loadingMore = false;
    $scope.loadMore = function() {
        if (loadingMore) return;

        odaStatus.setStatus("Loading....");
        loadingMore = true;
        odaApi.getDisplayUnits(master.short_name, master.revision, maxAddress).success(function(data){
            loadingMore = false;
            odaStatus.setStatus("Loaded");
            $scope.displayUnits = $scope.displayUnits.concat(data);
            maxAddress = $scope.displayUnits[$scope.displayUnits.length-1].offset;
        });
    }

    var commentsRequest = odaApi.getComments(master.short_name, master.revision);
    var functionsRequest = odaApi.getFunctions(master.short_name, master.revision);
    var labelsRequest = odaApi.getLabels(master.short_name, master.revision);
    var symbolsRequest = odaApi.getSymbols(master.short_name, master.revision);
    $q.all([commentsRequest, functionsRequest, labelsRequest, symbolsRequest]).then(function(results) {
        $scope.comments = {};
        $scope.functions = {};
        $scope.labels={};
        $scope.symbols={};

        comments = results[0];
        functions = results[1];
        labels = results[2];
        symbols = results[3];

        $.each(comments.data, function(i,comment){
            $scope.comments[comment.offset] = comment;
        });

        $.each(functions.data, function(i,func){
            $scope.functions[func.offset] = func;
        });

        $.each(labels.data, function(i, label){
            $scope.labels[label.offset] = label;
        });

        $.each(symbols.data, function(i, symbol){
            $scope.symbols[symbol.offset] = symbol;
        });

        loadDisassembly();
    });

    $scope.getLabel = function(offset) {
        var labelLookup = $scope.labels[offset];
        var symbolLookup = $scope.symbols[offset];

        if (typeof labelLookup != 'undefined') {
            label = labelLookup.label;
        } else
        if (typeof symbolLookup != 'undefined') {
            label = symbolLookup.name;
        } else {
            // it's not a local label or function we know about, so assume it's a draffy local label
            label = 'loc_' + offset.toString(16);
        }

        return label;

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

    $scope.hasTargetRef = function(du) {
        return du.targetRef != null;
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
    };

    $scope.$on('position', function(event, position) {
        console.log('position changed' + position);

        var handleScroll = function() {
            var id = "addr-" + $scope.location;
            if (!$("#"+id).exists() || !$("#"+id).visible()) {
                $location.hash(id);
                // call $anchorScroll()
                $anchorScroll();
            }
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
    });

    $scope.retvalEnter = function($event, du) {
        var func = $scope.functions[du.offset];
        if ( undefined == func ) {
            func = {
                args : 'unknown',
                name : $scope.getLabel(du.offset)
            };
        }

        func.retval = $($event.target).text();
        $scope.functions[du.offset] = func;

        $http.post("/odaweb/api/functions/",{
            object_id : oda_util.getMaster().object_id,
            content_type: oda_util.getMaster().content_type,
            retval: func.retval,
            args: func.args,
            name: func.name,
            offset: du.offset
        });

        //socketService.sendRetval(label, displayUnit.offset);
        $event.preventDefault();
    };

    $scope.argsEnter = function($event, du) {
        var func = $scope.functions[du.offset];
        if ( undefined == func ) {
            func = {
                retval : 'unknown',
                name : $scope.getLabel(du.offset)
            };
        }

        func.args = $($event.target).text();
        $scope.functions[du.offset] = func;

        $http.post("/odaweb/api/functions/",{
            object_id : oda_util.getMaster().object_id,
            content_type: oda_util.getMaster().content_type,
            retval: func.retval,
            args: func.args,
            name: func.name,
            offset: du.offset
        });

        //socketService.sendRetval(label, displayUnit.offset);
        $event.preventDefault();
    };

    $scope.hightlightLine = function(du) {
        odaApi.setPosition(du.offset);
    }

    $scope.labelEnter = function($event, displayUnit) {
        var label = $($event.target).text();

        var existingLabel = $scope.labels[displayUnit.offset];

        if (typeof existingLabel == 'undefined') {
            $http.post("/odaweb/api/labels/",{
                object_id : oda_util.getMaster().object_id,
                content_type: oda_util.getMaster().content_type,
                label: label,
                offset: displayUnit.offset
            }).success(function(data){
                $scope.labels[displayUnit.offset] = data;
            });

        } else {
            odaApi.setLabel(existingLabel.id, label);
        }

        socketService.sendLabel(label, displayUnit.offset);
        $event.preventDefault();
    };

    $scope.commentEnter = function($event, displayUnit) {
        var comment = $($event.target).text()

        var existingComment = $scope.comments[displayUnit.offset];

        if (typeof existingComment == 'undefined') {
            $http.post("/odaweb/api/comments/",{
                object_id : oda_util.getMaster().object_id,
                content_type: oda_util.getMaster().content_type,
                comment: comment,
                offset: displayUnit.offset
            }).success(function(data){
                $scope.comments[displayUnit.offset] = data;
            });
        } else {
            odaApi.setComment(existingComment.id, comment);
        }

        $scope.comments[comment.offset] = {comment: comment.comment, offset: displayUnit.offset};
        socketService.sendComment(comment, displayUnit.offset);
        $event.preventDefault();
    };

});