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

var StatusBar = function(odbFile) {
    this.setAddress = function(address) {
        $('.ace_status-indicator').html("0x" + address.toString(16));
    };

    var projectNameTemplate = Handlebars.compile('{{odaMaster.project_name}} : {{odaMaster.binary.arch}} ({{odaMaster.binary.size}})');
    $('.oda_status-name-box').html(projectNameTemplate({
        odaMaster: odbFile.oda_master
    }));

    this.defaultTemplateString = "[{{mode}}] {{status}}";
    this.updateTemplateString = '[{{mode}}] <span style="background-color:#00842D; color:white;">{{status}}</span>';
    var defaultStatus = 'ONLINE DISASSEMBLER 4EVER!';
    this.status = 'ONLINE DISASSEMBLER 4EVER!';

    var mode = 'normal';

    this._setStatus = function(templateString){
        var template = Handlebars.compile(templateString);
        var renderedText = template({mode:mode, status: this.status});
        $('.status-mode').html(renderedText);
    };
    this._setStatus(this.defaultTemplateString);


    var timer = null;
    this.pushStatus = function(newStatus) {
        this.status = newStatus;
        this._setStatus(this.updateTemplateString);
        if (timer != null) {
            clearInterval(timer);
        }
        timer = setTimeout(function(){
            timer = null;
            this.status = defaultStatus;
            this._setStatus(this.defaultTemplateString);
        }.bind(this), 5000);

    }




    var ajaxOuts = 0;
    $( document ).ajaxSend(function(e, jqXHR, ajaxOptions){
        if (ajaxOuts == 0) {
            $('.oda_loading-indicator').fadeOut(250).fadeIn(250).fadeOut(250).fadeIn(250);
        }
        ajaxOuts +=1;
        //console.log("ajaxSend", e, jqXHR, ajaxOptions);
    } );
    $( document ).ajaxSend(function(e, jqXHR, ajaxOptions){
        ajaxOuts -= 1;
        if (ajaxOuts == 0) {
            $('.oda_loading-indicator').fadeOut(500);
        }
    });

    var errorTemplate = Handlebars.compile("<p>{{time}}: {{thrownError}} -- {{url}}</p>");
    $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError){
        $('.oda_error-indicator').fadeIn(250);
        console.log(jqXHR, ajaxSettings.url, thrownError);
        var d = new Date();
        $('.oda-error-messages').append(errorTemplate({
            thrownError: thrownError,
            url: ajaxSettings.url,
            time: d.getHours() + ":" + d.getMinutes() + ":" + d.getSeconds() + "." + d.getMilliseconds()
        }));
    });

    $('.oda_error-indicator').click(function(){
        $('#messages-container').slideToggle();
    });
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
        /*if (odbFile.oda_master.binary.liveMode) {
            odbFile.duLength(function (length) {
                if ( length != 0 ) {
                    //editor.getSession().getDocument().setLength(length);
                    //windowLoader.reload(true);
                }
            });
        } else {
           // windowLoader.reload();
        }*/


    });

    /*editor.addEventListener('dblclick', function(e, editor){
        //console.log("dblclick");
        var cursor = editor.selection.getCursor();
        e.preventDefault();
        //console.log(editor.getSession().getTokenAt(cursor.row,cursor.column));
        var xrefLocation = $.grep(editor.getSession().getTokens(cursor.row), function(token){
            return token.type=='xref-location';
        });

        if (xrefLocation.length > 0){
            var targetRef = odaSession.getRowData(cursor.row).data.targetRef;
            var targetRefOffset;
            if (targetRef != null) {
                targetRefOffset = targetRef.offset;
            } else {
                targetRefOffset = parseInt(xrefLocation[0].value.substring(2),16);
            }
            console.log("xref-location", targetRefOffset);
            var xrefdecimal = targetRefOffset;
            odaSession.moveToOffset(xrefdecimal);
        }


        return "null";
    });*/

    odaApplication.value('odbFile', odbFile);
    odaApplication.value('editor', editor);
    odaApplication.value('odaSession', null);
    odaApplication.value('addrBar', addrBar);
    odaApplication.value('statusBar', statusBar);

    //Keyboard Handling
    odaApplication.run(function($rootScope){
       /* editor.setKeyboardHandler(function(data, hashId, key, keyCode, e) {
            // ignore command keys (shift, ctrl etc.)
            if (hashId !== 0 && (!key || keyCode == -1))
                return null;

            //Arrow Keys
            if (keyCode >=33 && keyCode <= 40 ) {
                return null;
            }

            var session = editor.getSession();

            var cursor = session.getSelection().getCursor();
            var line = session.getDocument().getLineData(cursor.row);

            console.log("keyboard", data, hashId, key, keyCode, e);
            return {
                command: {
                    passEvent: true,
                    exec: function() {return true;}
                }

            };
        });*/
    });

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

odaApplication.run(function($rootScope, $modal, odbFile, editor){
    $rootScope.$on('command.comment', function(event, line){
        editor.focusActive('.comment');
        /*var scope = $rootScope.$new(true);
        scope.line = line;

        console.log("LINE", line);
        var modalInstance = $modal.open({
          templateUrl: 'commentModal.html',
          controller: 'CommentController',
          size: 'lg',
          scope: scope
        });

        focus('comment');

        modalInstance.result.then(function(data){
            odbFile.addComment(line.line.data.offset, data.comment);
        });*/

    });

    $rootScope.$on('command.dataToCode', function(event,data){
        if (data.isCode) {
            return;
        }

        odbFile.makeCode(data.offset);
    });


    $rootScope.$on('command.codeToData', function(event, data){
        if (!data.isCode) {
            return;
        }

        odbFile.makeData(data.offset);
    });


    $rootScope.$on("command.makeFunction", function(event, data) {
        if (!data.isCode) {
            return;
        }

        var scope = $rootScope.$new(true);

        var offset = data.offset
        var hex = intToHex(offset);

        scope.odbFile = odbFile;

        var existingFunc = odbFile.functions[offset];

        scope.data = {
            function: {
                name: 'FUNCTION_' + hex,
                retval: 'unknown',
                args: 'unknown'
            }
        };
        scope.data.offsetHex = hex;
        scope.data.modify = (existingFunc != null);

        if(existingFunc != null) {
            scope.data.function.name = existingFunc.name;
            scope.data.function.retval = existingFunc.retval;
            scope.data.function.args = existingFunc.args;
        }

        var modalInstance = $modal.open({
          templateUrl: 'makeFunction.html',
          controller: 'MakeFunctionController',
          size: 'lg',
          scope: scope
        });

        modalInstance.result.then(function(funcDef){
            if (existingFunc != null) {
                console.log('update function', existingFunc);
                odbFile.updateFunction(offset, scope.data.function.name,
                    scope.data.function.retval, scope.data.function.args);
            } else {
                console.log('create function', funcDef);

                odbFile.createFunction(offset, scope.data.function.name,
                    scope.data.function.retval, scope.data.function.args);
            }

        });
    });

    $rootScope.$on("command.makeStructType", function(event, data) {
        var scope = $rootScope.$new(true);

        scope.odbFile = odbFile;

        scope.data = {
            structData: {
                name: 'StructName',
                is_packed: true
            }
        };

        var modalInstance = $modal.open({
          templateUrl: 'makeStructType.html',
          controller: 'MakeStructTypeController',
          size: 'lg',
          scope: scope
        });

        modalInstance.result.then(function(structDef){
            console.log('create structure type');
            odbFile.addStructType(scope.data.structData.name);
        });
    });

    $rootScope.$on("command.makeStructVariable", function(event, data) {
        var line= data.line;

        var scope = $rootScope.$new(true);

        var offset = line.data.offset;

        scope.line = line;

        scope.odbFile = odbFile;
        scope.structTypes = odbFile.structTypes;

        scope.data = {
            structData: {
                offset: offset,
                name: 'StructVarName',
                type: odbFile.structTypes[0].name,
                types: odbFile.structTypes
            }
        };

        var modalInstance = $modal.open({
          templateUrl: 'makeStructVariable.html',
          controller: 'MakeStructVariableController',
          size: 'lg',
          scope: scope
        });

        modalInstance.result.then(function(structDef){
            console.log('create structure variable');
            odbFile.addStructVariable(scope.data.structData.offset, scope.data.structData.name, scope.data.structData.type);
        });
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

    odbFile.on('loaded', function (odbFile) {
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
            template: '/static2/templates/symbols.html'
        }, {
            icon: 'fa-font',
            template: '/static2/templates/strings.html'
        }, {
            icon: 'fa-search',
            template: '/static2/templates/find_results.html'
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

odaApplication.controller('NavbarController', function NavbarController($scope, Docker, $modal, $location,
                                                                        fileUpload, AuthService, odbFile,
                                                                        focus){
    $scope.examples = window.examples;

    $scope.a = function() {return true;};

    $scope.loadExample = function(example) {
        window.location = "/odaweb/" + example.short_name;
    };

    $scope.openFile = function() {
        var modalInstance = $modal.open({
          templateUrl: 'uploadFileModal.html',
          controller: 'UploadFileController',
          size: 'lg'
        });

        modalInstance.result.then(function(data){
            console.log('ok', data);

            $scope.configureFile(data);

        });
    };

    $scope.downloadDisassembly = function() {
        window.location = '/odaweb/_download?short_name=' + odbFile.shortName + '&revision=' + odbFile.revision;
    };

    $scope.goToAddressPrompt = function() {
        var modalInstance = $modal.open({
          templateUrl: 'gotoAddressModal.html',
          controller: 'GotoAddressController',
          size: 'md'
        });

        focus("goto");

        modalInstance.result.finally(function(data){
            console.log(data);
            $("#goto-textbox").blur();
        });

    };

    $scope.findSequence = function() {
        Docker.select(Docker.docks[2]);
    };

    $scope.$on('command.goto', function(event) {
        $scope.goToAddressPrompt();
    });

    $scope.connectedUsers = [];
    $scope.$on('user.connect', function(event, username){
        console.log('user.connect', event, username);
        $scope.$apply(function(){
            $scope.connectedUsers.push({
                username: username,
                color: '#'+Math.floor(Math.random()*16777215).toString(16)
            });

        });
    });

    $scope.$on('user.disconnect', function(event, username) {
        console.log('user.disconnect', event, username);
        $scope.$apply(function(){
            for (var i=$scope.connectedUsers.length-1; i>=0; i--) {
                if ($scope.connectedUsers[i].username === username) {
                    $scope.connectedUsers.splice(i, 1);
                    break;
                }
            }
        });
    });


    $scope.$on('command.open', function(event) {
        $scope.openFile();
    });

    $scope.share = function(){
        odbFile.connectLink().success(function(shareData){
            var modalInstance = $modal.open({
                templateUrl: 'shareLive.html',
                controller: 'ShareLiveController',
                resolve: { shareInfo: function() { return shareData; } },
                size: 'lg'
            });
        });
    };

    var monitorSandbox = function(shortName, revision) {
        var modalInstance = $modal.open({
          templateUrl: 'monitorSandbox.html',
          controller: 'MonitorSandboxController',
          resolve: { fileInfo: function(){return {shortName: shortName, revision:revision};} },
          size: 'lg'
        });
    };

    $scope.configureFile = function(fileData) {
        console.log(fileData);
        var modalInstance = $modal.open({
          templateUrl: 'configureFileModal.html',
          controller: 'ConfigureFileController',
          resolve: { fileData : function() {return fileData;} },
          size: 'lg'
        });

        modalInstance.result.then(function(data){
            if (data.sandbox) {
                monitorSandbox(data.shortName, data.revision);
            } else {
                console.log(data, fileData);
                window.location = "/odaweb/" + fileData.short_name;
            }
        });
    };

    $scope.saveAndRedirect = function() {
        odbFile.save().success(function(data){
            window.location = data.url;
        });
    };

    $scope.loginPage = function() {
        window.location = "/accounts/login"
    };

    $scope.createAccount = function() {
        window.location = "/accounts/signup"
    };

    $scope.about = function() {
        var modalInstance = $modal.open({
          templateUrl: 'about.html',
          size: 'lg'
        });
    };

    $scope.whatsOda = function() {
        var modalInstance = $modal.open({
          templateUrl: 'whats-oda.html',
          controller: 'WhatsOdaController',
          size: 'lg'
        });
    };
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

var ConfigureFileController = function($scope, $modalInstance, $http, fileData) {

    console.log('ConfigureFileController', fileData);

    $scope.loading = false;

    $scope.data = {
        fileData: fileData,
        sandbox: false
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function () {

        $scope.loading = true;

        var computeSelected = function(platformOptions) {
            var selected = [];
            for (var i=0; i<platformOptions.length; i++) {
                if (platformOptions[i].selectedValue != 'DEFAULT') {
                    selected.push(platformOptions[i].selectedValue);
                }
            }
            return selected;
        };

        var options = computeSelected($scope.options.platformOptions);
        console.log('options', options);

        var options = {
            architecture: $scope.options.architecture,
            base_address: $scope.options.base_address,
            endian: $scope.options.endian,
            selected_opts: computeSelected($scope.options.platformOptions)
        };

        OdbFile.setOptionsFor(fileData.short_name, fileData.revision, options)
            .success(function(){
            $modalInstance.close({
                sandbox: $scope.data.sandbox,
                shortName: fileData.short_name,
                revision: fileData.revision

            });
        });
    };

    var arch = fileData.arch;
    $scope.optionsTemplate = function() {
        var view = '/odaweb/optionsview?arch=' + arch
        return view;
    };

    $scope.options = {
        architecture: fileData.arch,
        endian: 'DEFAULT'
    };

    $scope.optionsUpdated = function() {
        console.log($scope.options);
    };

    /* determine if we support running the file in the sandbox */
    $scope.runtimeSupported = function() {
        var enabled = false;
        /* TODO: Add other targets that will run in the Windows XP VM */
        /* Disable all targets for now until we enable support for sandboxing
        if (fileData.target == 'pei-i386') {
            enabled = true;
        }
        */
        return enabled;
    };

    $scope.architectures = window.system.architectures;
    $scope.endians = window.system.endians;

    var updateArchitectureOptions = function() {
        $http.get('/odaweb/api/disassembler/0/options/?arch=' + $scope.options.architecture).success(function(data){            console.log('OPTIONS', data);
            $scope.options.platformOptions = data.options;
            $.each($scope.options.platformOptions, function(i, po){
                po.selectedValue = 'DEFAULT'
            });
        });
    };
    updateArchitectureOptions();

    $scope.$watch('options.architecture', function(){
        updateArchitectureOptions()
    });


    /** Platform Options Portion **/
    /*$http.get('/odaweb/api/disassembler/0/architectures/').success(function(data){
        $scope.architectures = data.architectures
        $scope.endians = data.endians
    });
    var updateArchitectureOptions = function() {
        $http.get('/odaweb/api/disassembler/0/options/?arch=' + $scope.options.architecture).success(function(data){
            console.log('OPTIONS', data);
            $scope.options.platformOptions = data.options;
            $.each($scope.options.platformOptions, function(i, po){
                po.selectedValue = 'DEFAULT'
            });
        });
    };
    updateArchitectureOptions();*/
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




/*
var OdaApplication = function() {
    this.editor = null;
    this.odaSession = null;
    this.odbFile = null;

    this.setEditor = function(editor) {
        this.editor = editor;
    };

    this.getEditor = function() {
        return this.editor;
    }

    this.setOdaSession = function(odaSession) {
        this.odaSession = odaSession;
    };

    this.getOdaSession = function() {
        return this.odaSession;
    }

    this.setOdbFile = function(odbFile) {
        this.odbFile = odbFile
    };

    this.getOdbFile = function() {
        return this.odbFile;
    };

};


OdaApplication.prototype.getMaster = function() { return window.oda_master; };
OdaApplication.prototype.getUsername = function() { return window.user.username};
OdaApplication.prototype.getSectionInfo = function() { return window.oda_master.section_info;}

var oda_util = new OdaApplication();

*/
