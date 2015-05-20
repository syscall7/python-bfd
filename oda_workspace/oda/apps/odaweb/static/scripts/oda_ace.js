"use strict";

var Section = function(sectionDescriptor) {
    $.extend(this,sectionDescriptor);

    this.isCode = function() {
        for (var i=0; i<this.flags.length; i++) {
            if (this.flags[i].name == 'SEC_CODE') {
                return true;
            }
        }
        return false;
    };

    this.isData = function() {
        return !this.isCode();
    };

    return this;


};

var intToHex = function(value){
    var stringValue = value.toString(16);
    var s = "000000000" + stringValue;
    return s.substr(s.length-8);

};

Handlebars.registerHelper("hex", intToHex);

Handlebars.registerHelper("pad", function(value, length) {
    var counter = length - value.length;
    for(var i=0; i<counter; i++) {
        value = value.concat("&nbsp;");
    }
    return value;
});

Handlebars.registerHelper("formatSectionOffset", function(section, offset, length) {
    var value = section + ":" + intToHex(offset);
    var counter = length - value.length;
    for(var i=0; i<counter; i++) {
        value = "&nbsp;".concat(value);
    }
    return value;
});

var odaApplication = angular
    .module('odaApp',['ngSanitize', 'ui.bootstrap', 'ui.keypress'])
    .config(function($httpProvider) {

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

});

function start(odbFile) {

    var editor = CreateInstructionTable(odbFile);

    var addrBar = new AddressNavBar('#addr-bar-canvas', odbFile.sections, odbFile.parcels);

    addrBar.onChange(function(address) {
        editor.gotoAddress(address);
        console.log('My change handler: ' + address.toString(16));
    });



    var statusBar = new StatusBar(odbFile);

    editor.onViewportChanged.subscribe(function (e, args) {
        //console.log("ODA_ACE VIEWPORT CHANGED", e, args);
    });

    editor.activeAddressChanged.subscribe(function(e, args) {
        //console.log("activeAddressChanged", e, args);
        addrBar.setAddress(args.offset);
        statusBar.setAddress(args.offset);
    });

    /*odaSession.on('cursor.change', function(e) {
        var offset = e.offset;
        console.log("CURSOR CHANGE", offset);
        addrBar.setAddress(offset);
        statusBar.setAddress(offset);
    })*/



    odbFile.on(ODB_EVENTS.CHANGED, function(e){
        console.log("odbFile.on('ODB_EVENTS.CHANGED')", e);
        editor.reload();
    });



    odaApplication.value('odbFile', odbFile);
    odaApplication.value('editor', editor);
    odaApplication.value('odaSession', null);
    odaApplication.value('addrBar', addrBar);
    odaApplication.value('statusBar', statusBar);

    angular.bootstrap(document, ['odaApp']);

}

odaApplication.run(function($rootScope, statusBar){
    $rootScope.$on('user.connect', function(e, username){
        //console.log('user.connect', e);
        statusBar.pushStatus("USER " + username + " HAS CONNECTED...");
    });
});

odaApplication.run(function(odbFile, addrBar){
    odbFile.on(ODB_EVENTS.PARCELS_RELOADED, function(){
        addrBar.setParcels(odbFile.parcels);
    });

});


var MakeFunctionController = function($scope, $modalInstance) {

    $scope.ok = function() {
        $modalInstance.close($scope.data.structData);
    };


    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
};

var MakeStructTypeController = function($scope, $modalInstance) {

    $scope.ok = function() {
        $modalInstance.close($scope.data.function);
    };


    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
};

var MakeStructVariableController = function($scope, $modalInstance) {

    $scope.ok = function() {
        $modalInstance.close($scope.data.function);
    };


    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
};

var CommentController = function($scope, $modalInstance) {
    $scope.comment = {
        text: ""
    }

    $scope.save = function () {
        $modalInstance.close({
            comment: $scope.comment.text
        });
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

};

odaApplication.run(function($rootScope, Docker, odbFile, editor) {
    odbFile.on(ODB_EVENTS.LIVE_ENTRY_UPDATE, function (event, liveEntryText) {
        //var odaSession = oda_util.getOdaSession();
        //var odbFile = oda_util.getOdbFile();
        if (editor != null && odbFile != null) {
             editor.reload();
        }
    });
});


function handleSaveButton(options) {

    if (options.saved) {
        toastr.options = { positionClass: 'toast-top-full-width', closeButton: true, timeOut: 15000 }
        toastr.success('You can share this url:</p><a href="' + window.location + '">' +
            window.location + "</a><p><p>If you make more changes, hit <strong>share</strong> again to get a new link.");
    }
   /* if (options.saved) {

        // show the popover, but don't close it when clicked
        $('#menu-item-share').popover('show').click(function(evt) {
            evt.stopPropagation();
            $(this).popover('show');
        });

        // close the popover when clicked anywhere outside the popover
        setTimeout(function(){
            $('html').click(function() {
                $('#menu-item-share').popover('hide');
            });
        }, 500);
    } */
}

function startOda() {

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            var csrftoken = $.cookie("csrftoken");
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var top = parseInt($('.theeditor').css('top'));
    var bottom = parseInt($('.theeditor').css('bottom'));
    $('#editor').height($(window).height() - top - bottom - 65);
    $(window).resize(function () {
        $('#editor').height($(window).height() - top - bottom - 65);
    });


    var odbFile = new OdbFile(window.oda_master);

    odbFile.load();

    odbFile.on(ODB_EVENTS.LOADED, function (odbFile) {
        $('loading-spinner').hide();
        $('.theeditor').show();


        $('.theeditor').layout({
            west__size: 41,
            west__closable: false,
            west__resizable: false,
            west__spacing_open: 0,
            west__spacing_closed: 0,
            center__childOptions: {
                spacing_open: 2,
                spacing_closed: 2,
                //closable: false,
                west__size: 400
            },
            east__initClosed: true,
            east__minSize: 150,

            spacing_open: 2,
            spacing_closed: 2
        });

        start(odbFile);

    });


    handleSaveButton({saved: window.saved});

}



odaApplication.filter('hex', function () {
    return function (num, len) {
        var numStr = num.toString(16);
        len = parseInt(len, 10);
        if (isNaN(num) || isNaN(len)) {
            return n;
        }
        numStr = ''+numStr;
        while (numStr.length < len) {
            numStr = '0'+numStr;
        }
        return numStr;
    };
});

/*odaApplication.factory('odaStatus', function($rootScope, $q, $http) {
    var status= {
        text: 'Loaded'
    };
    return {
        getStatus : function() {
            return status;
        },
        setStatus : function(newStatus) {
            status.text = newStatus;
        }

    };
});*/

odaApplication.service('CursorPosition', function(){

});

odaApplication.service('Docker', function(odbFile) {
    var master = odbFile.oda_master;

    this.docks = [];
    if (master.binary.liveMode) {
        this.docks.push({
            icon: 'fa-briefcase',
            template: 'live_entry.html'
        });
        this.activeDock = this.docks[0];
    } else {
        this.docks.push({
            icon: 'fa-list',
            template: 'symbols.html'
        }, {
            icon: 'fa-font',
            template: 'strings.html'
        }, {
            icon: 'fa-search',
            template: 'find_results.html'
        }, {
            icon: 'fa-text-width',
            template: 'structform.html'
        });
        this.activeDock = this.docks[0];
    }

    /*this.docks.push({
        icon: 'fa-th-large',
        template: '/static2/templates/sections.html'
    });*/

    this.select = function(thing) { this.activeDock = thing; };
    this.clear = function(thing) { this.activeDock = null; };
});

odaApplication.controller('DockMenuController', function DockMenuController($scope, $http, $window, Docker) {

    $scope.isActive = function(dock) {
        return Docker.activeDock == dock;
    };
    $scope.Docker = Docker;

});

odaApplication.controller('DockController', function DockController($scope, $http, $window, Docker) {

    $scope.isActive = function(dock) {
        return Docker.activeDock == dock;
    };
    $scope.Docker = Docker;

});


var WhatsOdaController = function($scope, $modalInstance) {
    $scope.data = {
        architectures: window.system.architectures
    };
    $scope.close = function () {
        $modalInstance.close();
    };
};

var ShareLiveController = function($scope, $modalInstance, $location, shareInfo) {
    console.log("share info ", shareInfo);

    $scope.shareInfo = shareInfo;

    $scope.shareUrl = function() {
        return $location.protocol() + "://" + $location.host() +":" + $location.port() + shareInfo.shareUrl;
    };

    $scope.ok = function () {
        $modalInstance.close();
    };

};

var UploadFileController = function($scope, $modalInstance, fileUpload){

    //http://stackoverflow.com/questions/18716113/scope-issue-in-angularjs-using-angularui-bootstrap-modal
    $scope.data = {
        projectName: null
    };

    $scope.$watch('uploadFile', function() {
        if ($scope.uploadFile && $scope.data.projectName == null) {
            $scope.data.projectName = $scope.uploadFile.name;
        }
    });



    $scope.ok = function () {
        $scope.loading = true;

        fileUpload.uploadFileToUrl( $scope.uploadFile, $scope.data.projectName, '/odaweb/_upload')
            .success(function(data){
            $modalInstance.close(data);
        }).error(function(data){
            // default error message
            var err_msg = 'There was a problem with the upload.  Maximum upload size is 256KB.';
            if (data.error) {
                err_msg = data.error;
            }
            $scope.loading = false;
            $scope.error = err_msg;
        });

        /* $modalInstance.close({
            projectName: $scope.data.projectName,
            uploadFile: $scope.uploadFile
        }); */
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

};

var MonitorSandboxController = function($scope, $interval, $http, fileInfo) {
    var checking;
    var UPDATE_INTERVAL = 3000;
    $scope.elapsedSeconds = 0;
    $scope.job_status = null;

    $http.post('/odaweb/api/sandbox/1/submit/', {
        short_name: fileInfo.shortName,
        revision: fileInfo.revision
    }).success(function(job){
        checking = $interval(function(){
            console.log('checking...');

            if (!$scope.jobDone()) {
                $scope.elapsedSeconds += UPDATE_INTERVAL;
            }

            $http.get('/odaweb/api/sandbox/1/status/', {
                params: {
                    short_name: fileInfo.shortName,
                    revision: fileInfo.revision
                }
            }).success(function(response) {
                $scope.job_status = response.status

            });
        }, UPDATE_INTERVAL);
    });

    $scope.jobDone = function() {
        var done = false;
        if ($scope.job_status) {
            done = $scope.job_status.status == "reported";
        }
        return done;
    }

    $scope.continue = function () {
        window.location = "/odaweb/" + fileInfo.shortName;
    };

};



var GotoAddressController = function($scope, $modalInstance, editor) {

    $scope.data = {
        address: null
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function () {
        var position = parseInt($scope.data.address.substring(2),16);
        console.log('set position', position);
        editor.gotoAddress(position);
        $modalInstance.close({address: $scope.data.address});
    };

};

odaApplication.service('Session', function(){
    this.create = function(userId) {
        this.userId = userId;
    };
});

odaApplication.factory('AuthService', function($http, Session){

    return {
        login: function(credentials) {
            return $http({
                method: 'POST',
                url: '/odaweb/login',
                data: $.param(credentials),
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).then(function(response){
                var data = response.data;
                Session.create(data.userId);
                return data;
            });
        },
        isAuthenticated: function() {
            return !!Session.userId
        },
        logout: function() {
            return $http({
                method: 'POST',
                url: '/accounts/logout/'
            }).then(function(){
                location.reload();
            });
        }

    };
});

odaApplication.run(function($rootScope, AuthService, Session){

    $rootScope.isAuthenticated = AuthService.isAuthenticated;

    $rootScope.currentUser = null;

    $rootScope.setCurrentUser = function (user) {
        $rootScope.currentUser = user;
    };

    $rootScope.login = function (credentials) {
        AuthService.login(credentials).then(function (user) {
            AuthService.isAuthenticated();
            $rootScope.setCurrentUser(user);
            console.log("logged in", user);
        });
    };

    $rootScope.logout = function() {
        AuthService.logout();
    }


    if (window.user.authenticated) {
        var username = window.user.username;
        console.log('Username: ',username);
        Session.create(username);
        $rootScope.setCurrentUser({username: username});
    }
});


odaApplication.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;

            element.bind('change', function(){
                scope.$apply(function(){
                    modelSetter(scope.$parent, element[0].files[0]);
                    console.log('fileModel change');
                });
            });
        }
    };
}]);

odaApplication.service('fileUpload', ['$http', function ($http) {
    this.uploadFileToUrl = function(file, project_name, uploadUrl){
        var fd = new FormData();
        fd.append('filedata', file);
        fd.append('project_name', project_name);
        return $http.post(uploadUrl, fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        });
    }
}]);


function showNotificationBar(message, duration, bgColor, txtColor, height) {

    /*set default values*/
    duration = typeof duration !== 'undefined' ? duration : 1500;
    bgColor = typeof bgColor !== 'undefined' ? bgColor : "#F4E0E1";
    txtColor = typeof txtColor !== 'undefined' ? txtColor : "#A42732";
    height = typeof height !== 'undefined' ? height : 40;
    /*create the notification bar div if it doesn't exist*/
    if ($('#notification-bar').size() == 0) {
        var HTMLmessage = "<div class='notification-message' style='text-align:center; line-height: " + height + "px;'> " + message + " </div>";
        $('body').prepend("<div id='notification-bar' style='display:none; width:100%; height:" + height + "px; background-color: " + bgColor + "; position: fixed; z-index: 100; color: " + txtColor + ";border-bottom: 1px solid " + txtColor + ";'>" + HTMLmessage + "</div>");
    }
    /*animate the bar*/
    $('#notification-bar').slideDown(function() {
        setTimeout(function() {
            $('#notification-bar').slideUp(function() {});
        }, duration);
    });
}


//To allow html to be present in the popovers
//http://stackoverflow.com/questions/16722424/how-do-i-create-an-angularjs-ui-bootstrap-popover-with-html-content/21979258#21979258
odaApplication.filter('unsafe', ['$sce', function ($sce) {
    return function (val) {
        return $sce.trustAsHtml(val);
    };
}]);

odaApplication.directive('focusOn', function() {
   return function(scope, elem, attr) {
      scope.$on('focusOn', function(e, name) {
        if(name === attr.focusOn) {
          elem[0].focus();
        }
      });
   };
});

odaApplication.factory('focus', function ($rootScope, $timeout) {
  return function(name) {
    $timeout(function (){
      $rootScope.$broadcast('focusOn', name);
    }, 250);
  }
});


// update popover template for binding unsafe html
angular.module("template/popover/popover.html", []).run(["$templateCache", function ($templateCache) {
    $templateCache.put("template/popover/popover.html",
      "<div class=\"popover {{placement}}\" ng-class=\"{ in: isOpen(), fade: animation() }\">\n" +
      "  <div class=\"arrow\"></div>\n" +
      "\n" +
      "  <div class=\"popover-inner\">\n" +
      "      <h3 class=\"popover-title\" ng-bind-html=\"title | unsafe\" ng-show=\"title\"></h3>\n" +
      "      <div class=\"popover-content\"ng-bind-html=\"content | unsafe\"></div>\n" +
      "  </div>\n" +
      "</div>\n" +
      "");
}]);