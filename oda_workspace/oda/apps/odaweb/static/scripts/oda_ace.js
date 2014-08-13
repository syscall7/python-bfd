var ace_document = ace.require('ace/document');
var oop = ace.require("ace/lib/oop");
var EventEmitter = ace.require("ace/lib/event_emitter").EventEmitter;

var OdbFile = function() {

    this.functions = [];

    this.sections = [];

    this.parcels = [];

    this.comments = [];

    this.displayUnitsLength = -1;

    this.shortName = null;


    this.load = function (shortName) {
        this.shortName = shortName;

        var fq = $.get('/odaweb/api/functions/', {
            short_name: this.shortName,
            revision: 0
        }).success(function (data) {
            for (var i = 0; i < data.length; i++) {
                this.functions[data[i].offset] = data[i];
            }
        }.bind(this));

        var sq = $.get('/odaweb/api/sections/', {
            short_name: this.shortName,
            revision: 0
        }).success(function (data) {
            this.sections = data;
        }.bind(this));

        var pq = $.get('/odaweb/api/parcels/', {
            short_name: this.shortName,
            revision: 0
        }).success(function (data) {
                this.parcels = data;
        }.bind(this));

        var dulenq = $.get('/odaweb/api/displayunits/1/size', {
            short_name: this.shortName,
            revision: 0
        }).success(function (data) {
            this.displayUnitsLength = data;
        }.bind(this));

        $.when(fq, sq, dulenq).done(function (data) {
            this._signal('loaded', this);
        }.bind(this));
    };

    this.duLength = function(callback) {
        $.get('/odaweb/api/displayunits/1/size', {
            short_name: this.shortName,
            revision: 0
        }).success(function (data) {
            this.displayUnitsLength = data;
            callback(data);
        }.bind(this));
    }

    this.loadDu = function (addr, numUnits, callback) {
        $.get('/odaweb/api/displayunits/', {
            short_name: this.shortName,
            revision: 0,
            addr: addr,
            logical: true,
            units: numUnits
        }).done(callback);
    };

    this.vmaToLda = function (vma, callback) {
        $.get('/odaweb/api/displayunits/1/vmaToLda', {
            short_name: this.shortName,
            revision: 0,
            vma: vma
        }).done(callback);
    };

    this.makeData = function (vma, callback) {
        console.log('makeData', vma);
        $.get('/odaweb/api/displayunits/1/makeData', {
            short_name: this.shortName,
            revision: 0,
            vma: vma
        }).success(callback)
    };

    this.makeCode = function (vma, callback) {
        console.log('makeCode', vma);
        $.get('/odaweb/api/displayunits/1/makeCode', {
            short_name: this.shortName,
            revision: 0,
            vma: vma
        }).success(callback)
    };

    this.addComment = function (offset, comment) {
        console.log("Comment", offset, comment);
        this.comments[offset] = {
            comment: comment,
            offset: offset
        }

        this._signal('changed', {
            addr: offset,
            action: 'insertComment'
        });
    };

    this.callbacks = {};
    this.on = function (name, handler) {
        if (!this.callbacks[name]) {
            this.callbacks[name] = $.Callbacks();
        }
        this.callbacks[name].add(handler);

    };
    this._signal = function (name, data) {
        if (!this.callbacks[name]) {
            this.callbacks[name] = $.Callbacks();
        }
        this.callbacks[name].fire(data);
    };

};

var OdaSession = function(editor, odbFile, windowLoader) {

    //this.cursorPositon = null;

    this.editor = editor;

    this.windowLoader = windowLoader;

    this.session = editor.getSession();

    this.odbFile = odbFile;

    this.onCursorChange = $.Callbacks();

    this.session.selection.on('changeCursor', function(e) {
        var cursor = this.session.getSelection().getCursor();

        //var line = session.getDocument().getLine(cursor.row);
        var lineData = this.session.getDocument().getLineData(cursor.row);
        if (!lineData) {
            //linedata can be null when window is not loaded...
            return;
        }
        var lineData = lineData.data;

        try {
            var offset = lineData.offset;
            this.onCursorChange.fire(offset);
        } catch (ex) {
            console.log(ex);
        }

    }.bind(this));

    this.getRowData = function(row) {
        return this.session.getDocument().getLineData(row);
    };

    this.findRowForAddress = function(address) {
        var line = -1;
        for(line=0; line<this.session.getDocument().window.lines.length; line++) {
            //Ugh, this is brittle, relies on window.lines to have a data.offset...
            if (this.session.getDocument().window.lines[line].data.offset == address)
                break;
        }

        if (line == this.session.getDocument().window.lines.length) {
            console.log('findRowForAddress outside window', address);
            return -1;
        }

        var lineToMoveTo = this.session.getDocument().window.startRow + line + 1;
        console.log('findRowForAddress',address, lineToMoveTo);
        return lineToMoveTo;
    };

    this.moveToOffset = function(offset) {
        //TODO debounce this
        var odaSession = this;

        var line = this.findRowForAddress(offset);
        if (line == -1) {
            odaSession.odbFile.vmaToLda(offset, function(ldu){
                odaSession.windowLoader.once('loaded', function(){
                    setTimeout(function(){
                        console.log('fixup');
                        var lineToMoveTo = odaSession.findRowForAddress(offset);
                        odaSession.editor.gotoLine(lineToMoveTo, 0, false);
                    }, 10);

                });

            editor.gotoLine(odaSession.windowLoader.displayUnitToRow(ldu), 0);
            });
        } else {
            odaSession.editor.gotoLine(line, 0, false);
        }
    }

};

var CommentDialog = function(du) {
    var modalId = "#my-modal";
    var saveButtonId = "#my-modal .btn-primary";

    $('#my-modal .commentLine').text(du.offset);
    $(modalId).unbind().on('shown.bs.modal', function (e) {
        // do something...
        $('#my-modal .comment-text').focus();
    });

    this.closeHandler = $.Callbacks();

    $(modalId).on('hidden.bs.modal', function (e) {
        this.closeHandler.fire(false);
    }.bind(this));

    this.save = function() {
        this.modal.modal('hide');
        var comment = $('#my-modal .comment-text').val();
        this.closeHandler.fire(true, comment);
    }

    $('#my-modal .comment-text').unbind().bind('keypress', function(e){
        if (e.charCode == '13') {
            this.save();
        }
    }.bind(this));

    this.modal = $('#my-modal').modal('show');


    $(saveButtonId).unbind().on('click', function () {
        this.save();
    }.bind(this));

};

function string_insert(original, index, string) {
  if (index > 0)
    return original.substring(0, index) + string + original.substring(index, this.length);
  else
    return string + original;
};

var StatusBar = function() {
    this.setAddress = function(address) {
        $('.ace_status-indicator').html("0x" + address.toString(16));
    };

    this.templateString = "[{{mode}}] ONLINE DISASSEMBLER 4EVER!";

    this.setMode = function(mode) {
        var template = Handlebars.compile(this.templateString);
        var renderedText = template({mode:mode});
        $('.status-mode').html(renderedText)
    };

    this.setMode('normal');
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


var KeyboardHandler = function(statusBar, odaSession, odbFile) {

    this.statusBar = statusBar;

    this.odaSession = odaSession;

    this.odbFile = odbFile;

    this.handler = function(data, hashId, key, keyCode, e) {
        // ignore command keys (shift, ctrl etc.)
        if (hashId !== 0 && (!key || keyCode == -1))
            return null;

        //Arrow Keys
        if (keyCode >=33 && keyCode <= 40 ) {
            return null;
        }

        var editor = data.editor;
        var session = editor.getSession();

        var cursor = session.getSelection().getCursor();
        var line = session.getDocument().getLineData(cursor.row);


        //line can be null when loading...
        if (line) {

            if (key == ';') {


                var commentDialog = new CommentDialog(line.data);

                commentDialog.closeHandler.add(function (save, comment) {
                    if (save) {
                        odbFile.addComment(line.data.offset, comment);
                    }

                    editor.focus();
                });

            }

            if (key == 'd') {
                this.odbFile.makeData(line.data.offset, function(data){
                    this.odaSession.windowLoader.reload();
                }.bind(this));
            }

            if (key == 'c') {
                this.odbFile.makeCode(line.data.offset, function(data){
                    this.odaSession.windowLoader.reload();
                }.bind(this));
            }

        }
        console.log("keyboard", data, hashId, key, keyCode, e);
        return null; /*{
            command: "null"
        };*/

    }.bind(this);
};

var lineRenderer = function(stringBuilder, row, onlyContents, foldLine) {
    if (!foldLine && foldLine != false)
        foldLine = this.session.getFoldLine(row);


    var line = this.session.doc.getLine(row);
    /*if (foldLine)
        var tokens = this.$getFoldLineTokens(row, foldLine);
    else
        var tokens = this.session.getTokens(row);*/
    stringBuilder.push(
            "<div class='ace_line' style='height:",
                    this.config.lineHeight * (this.$useLineGroups() ? 1 :this.session.getRowLength(row)
                    ), "px'>"
    );

    stringBuilder.push(line);

    stringBuilder.push("</div>");

};

var Renderer = function(odbFile) {

    // TODO: Generate the padding size (35) dynamically based on the longest section name in view
    this.baseFunctionTemplateString =
       '<span class="offset">{{{formatSectionOffset section_name offset 35 }}}</span>&nbsp;&nbsp;' +
       '<span class="raw disassembly-cell">{{{pad " " 20}}}</span>&nbsp;&nbsp;';
    this.baseFunctionTemplate = Handlebars.compile(this.baseFunctionTemplateString);

    this.functionTemplate1 = Handlebars.compile(this.baseFunctionTemplateString +
        '<span class="instruction">; =============== F U N C T I O N ====================================</span>');

    this.functionTemplate2 = Handlebars.compile(this.baseFunctionTemplateString +
        '<span class="function-return">{{retval}}</span> <span class="function-name">{{name}}</span> <span class="function-args">({{args}})</span>');

    // TODO: Generate the padding size (35) dynamically based on the longest section name in view
    this.baseDuTemplateString =
        '<span class="offset">{{{formatSectionOffset section_name offset 35 }}}</span>';
    this.baseDuTemplate = Handlebars.compile(this.baseDuTemplateString +
        '&nbsp;&nbsp;<span class="raw disassembly-cell">{{{pad rawBytes 20}}}</span>&nbsp;&nbsp;<span class="instruction">{{{instStr}}}</span>');
    this.labelTemplate = Handlebars.compile(this.baseDuTemplateString + "{{{ pad '' 20}}} loc_{{ hex offset }}:");

    this.render = function(du) {

        if (odbFile.functions[du.offset]) {
      //      console.log("FUNCTION", du, functions[du.offset]);
            var rendered_lines = this.renderFunction(du, odbFile.functions[du.offset]);
            return rendered_lines;
        }

        return this.renderDu(du)

    };

    this.renderTargetRef = function(du) {
        var label = "0x" + du.targetRef.offset.toString(16);
        if (odbFile.functions[du.targetRef.offset]) {
            label =  odbFile.functions[du.targetRef.offset].name + '[<a href="" class="xref-location">0x' + intToHex(du.targetRef.offset) + '</a>]';
        }
        return label;
    };

    this.renderFunction =  function(du, func) {

        var theLines = [this.baseFunctionTemplate(du), this.functionTemplate1(du)];
        for (var i=0;i<du.crossRef.length; i++) {
            theLines.push(this.baseFunctionTemplate(du) + '; CODE XREF:<a href="" class="xref-location">0x' + intToHex(du.crossRef[i].offset) + '</a>');
        }
        theLines.push(this.baseFunctionTemplate(du));
        theLines.push(this.functionTemplate2($.extend({}, du, func)));
        theLines.push(this.baseDuTemplate(du));
        return theLines;
    };

    this.renderComment = function(du) {
        if (odbFile.comments[du.offset]) {
            return '   ;' + odbFile.comments[du.offset].comment;
        }
        return '';
    }

    this.renderDu = function(du) {
        var renderedText = this.baseDuTemplate(du);
        if (du.isBranch) {
            return [this.baseFunctionTemplate(du), this.labelTemplate(du), renderedText];
        } if (du.targetRef) {
            return [renderedText + this.renderTargetRef(du)]
        }
        else
            return [renderedText + this.renderComment(du)];
    };
};


var WindowLoader = function(renderer, odbFile) {
    oop.implement(this, EventEmitter);

    this.windowSize = 500;
    this.lineSizes = [];
    this.renderer = renderer;
    this.odbFile = odbFile;


    this.callbacks = {};
    this.lastRowNumload;



    this.reload = function(clear) {
        if (clear) {
            this.lineSizes = [];
        }
        this.load(this.lastRowNumload);
    };

    this.load = function(rowNum) {

        this.lastRowNumload = rowNum;
        var duNum = this.rowToDisplayUnit(rowNum);

        NProgress.start();

        console.log("Loading Row=",rowNum, ' duNum=',duNum);
        this.odbFile.loadDu(duNum, 400, function(data){
            NProgress.inc(0.4);
            var tlines = [];

            var scrollTop = this.session.getScrollTop();

            var addedLines = 0;

            for (var i=0; i<data.length; i++) {
                var renderedLines = this.renderer.render($.extend({},data[i], {duNum:i+duNum}));
                renderedLines = $.map(renderedLines, function(line) { return {row: line, data: data[i], num: i }});
                if (renderedLines.length != 1) {
                    if (!this.lineSizes[duNum+i])
                        addedLines += renderedLines.length - 1;

                    this.lineSizes[duNum + i] = renderedLines.length;

                    //fixup the branch lines
                    var branch = data[i].branch;
                    var branch_label = data[i].branch_label;

                    for (var j=0; j<renderedLines.length-1; j++) {
                        renderedLines[j].data = $.extend({}, renderedLines[j].data, {branch:branch_label});
                    }
                }


                tlines = tlines.concat(renderedLines);

            }
            NProgress.done();
            var currentWindow = new ace_document.Window(rowNum, tlines);
            this._signal("loaded", { window: currentWindow, additionalRows: addedLines });
           // callback(currentWindow, addedLines);

            this.session.setScrollTop(scrollTop);
        }.bind(this));


    };

    this.rowToDisplayUnit = function(row) {
        var total = 0;
        var i = 0;
        while (total < row) {
            if (this.lineSizes[i]) {
                total += this.lineSizes[i];
            } else {
                total += 1;
            }
            i += 1
        }

        return i;
    };

    this.displayUnitToRow = function(row) {
        var linesAdded = 0;
        for (var key in this.lineSizes) {
            if (parseInt(key) < row) {
                linesAdded += this.lineSizes[key] - 1; //TODO: Ugh, lineSizes is marked as 2 when there is 1 additional line
                                                       // so this should be row + linesAdded - ( NumberOf(Keys < row IN lineSizes)
            }
        }
        var actualLine = row + linesAdded;
        console.log("Mapped DU:",row," TO:", actualLine);
        return actualLine;
    };

    this.getWindowSize = function() {
        return this.windowSize;
    }
};


var OdaMode = function() {
    this.getTokenizer = function() {
        return {
            getLineTokens : function(line, state, row) {
                return {
                    state:'start',
                    tokens:$.map($(line), function(el) {
                        return {value: $(el).text(), type: $(el).attr('class')} ;
                    })
                };
            }
        };
    };

    this.createWorker = function() { };
};

function replaceAll(str, find, replace) {
  return str.replace(new RegExp(find, 'g'), replace);
}

var OdaGutterRenderer = function(odaSession) {

    this.odaSession = odaSession;

    this.getText = function(session, row) {
        var rowData = odaSession.getRowData(row);
        if (rowData) {
            //console.log(rowData.data);
            var t = Handlebars.compile('{{{branch}}}')(rowData.data);
            //return rowData.data.branch;
            var k = '"' + replaceAll(replaceAll(replaceAll(rowData.data.branch, '&#x', '\\u'),'&nbsp;',''),';','') + '"';

            return JSON.parse(k);
            //return '\u2001\u2501\u25b6';
        } else {
            return '';
        }
    }.bind(this);

    this.getWidth = function(session, lastLineNumber, config) {
        return config.characterWidth * 6;
    };
};

var odaApplication = angular
    .module('odaApp',['ngSanitize', 'ui.bootstrap'])
    .config(function($httpProvider) {

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

});

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


function start(odbFile) {
    var editor;

    var renderer = new Renderer(odbFile);
    var windowLoader = new WindowLoader(renderer, odbFile);

    var addrBar = new AddressNavBar('#addr-bar-canvas', odbFile.sections, odbFile.parcels);

    addrBar.onChange(function(address) {
        odbFile.vmaToLda(address, function(ldu){
            editor.moveCursorToPosition({
                row:windowLoader.displayUnitToRow(ldu),column:0
            });
            editor.clearSelection();
        });
        console.log('My change handler: ' + address.toString(16));
    });

    var doc = new ace_document.OnlineDocument(odbFile.displayUnitsLength, windowLoader);

    doc.setLoadingString("..");
    editor = ace.edit("editor", doc);
    window.theeditor = editor;
    editor.setTheme("ace/theme/chrome");
    editor.setLineRenderer(lineRenderer);
    editor.getSession().setMode("ace/mode/javascript");
    editor.getSession().setMode(new OdaMode());
    editor.getSession().setUseWorker(false);
    editor.setShowPrintMargin(false);
    editor.renderer.setShowGutter(true);
    var odaSession = new OdaSession(editor, odbFile, windowLoader);
    var statusBar = new StatusBar();
    var keyboardHandler = new KeyboardHandler(statusBar, odaSession, odbFile);

    windowLoader.session = editor.getSession();
    editor.getSession().gutterRenderer = new OdaGutterRenderer(odaSession);


    odaSession.onCursorChange.add(function(offset) {
        console.log("CURSOR CHANGE", offset);
        addrBar.setAddress(offset);
        statusBar.setAddress(offset);
    })

    editor.setKeyboardHandler(keyboardHandler.handler);

    odbFile.on('changed', function(e){
        console.log(e);
        windowLoader.reload();
    });

    editor.addEventListener('dblclick', function(e, editor){
        //console.log("dblclick");
        var cursor = editor.selection.getCursor();
        e.preventDefault();
        //console.log(editor.getSession().getTokenAt(cursor.row,cursor.column));
        var xrefLocation = $.grep(editor.getSession().getTokens(cursor.row), function(token){
            return token.type=='xref-location';
        });

        if (xrefLocation.length > 0){
            console.log("xref-location", xrefLocation[0].value);
            var xrefdecimal = parseInt(xrefLocation[0].value.substring(2),16);
            odaSession.moveToOffset(xrefdecimal);
        }


        return "null";
    });

    oda_util.setEditor(editor);
    oda_util.setOdaSession(odaSession);
    oda_util.setOdbFile(odbFile);

    odaApplication.service('OdaSession', function() {
        this.odaSession = odaSession;

        this.getSession = function() {
            return this.odaSession;
        };

        this.setSession = function(odaSession) {
            this.odaSession = odaSession;
        };
    });


    angular.bootstrap(document, ['odaApp']);


}

odaApplication.run(function($rootScope, Docker){
    $rootScope.$on('liveEntryText', function(event, liveEntryText) {
        var odaSession = oda_util.getOdaSession();
        var odbFile = oda_util.getOdbFile();
        if (odaSession != null && odbFile != null) {
            //We have to get the new size here since the number of DUs could possibly have changed
            odbFile.duLength(function(length){
                oda_util.getEditor().getSession().getDocument().setLength(length);
                odaSession.windowLoader.reload(true)
            });


        }
    });

    //http://dmauro.github.io/Keypress/
    var listener = new window.keypress.Listener();
    listener.simple_combo("ctrl g", function() {
        console.log("You pressed ctrl g");
        //todo activate textbox
        $rootScope.$broadcast('command.goto');
    });

    listener.simple_combo("ctrl u", function(){
        $rootScope.$broadcast('command.open');
    });

    listener.simple_combo("ctrl f", function(){
        $rootScope.$apply(function(){Docker.select(Docker.docks[2]);});
    });
});

$(document).ready(function(){

    var top = parseInt($('.theeditor').css('top'));
    var bottom = parseInt($('.theeditor').css('bottom'));
    $('#editor').height($(window).height()-top-bottom - 5);
    $(window).resize(function(){
        $('#editor').height($(window).height()-top-bottom - 5 );
    });


    var odbFile = new OdbFile();
    odbFile.load(oda_util.getMaster().short_name);

    odbFile.on('loaded', function(odbFile){
        $('loading-spinner').hide();
        $('.theeditor').show();


        $('.theeditor').layout({
            west__size: 41,
            west__closable: false,
            west__resizable: false,
            west__spacing_open:0,
            west__spacing_closed:0,
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

});

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

odaApplication.factory('odaStatus', function($rootScope, $q, $http) {
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
});

odaApplication.service('Docker', function(odaApi) {
    var master = oda_util.getMaster();

    this.docks = [];
    if (master.binary.liveMode) {
        this.docks.push({
            icon: 'fa-briefcase',
            template: '/static2/templates/live_entry.html'
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
        });
        this.activeDock = this.docks[1];
    }

    this.docks.push({
        icon: 'fa-th-large',
        template: '/static2/templates/sections.html'
    });

    this.select = function(thing) { this.activeDock = thing; };
    this.clear = function(thing) { this.activeDock = null; };
});

odaApplication.controller('DockMenuController', function DockMenuController($scope, $http, $window, odaApi, Docker) {

    $scope.isActive = function(dock) {
        return Docker.activeDock == dock;
    };
    $scope.Docker = Docker;

});

odaApplication.controller('DockController', function DockController($scope, $http, $window, odaApi, Docker) {

    $scope.isActive = function(dock) {
        return Docker.activeDock == dock;
    };
    $scope.Docker = Docker;

});

odaApplication.controller('NavbarController', function NavbarController($scope, $modal, $location, fileUpload){
    $scope.examples = window.examples;

    $scope.loadExample = function(example) {
        window.location = "/oda/ace/" + example.short_name;
    };

    $scope.openFile = function() {
        var modalInstance = $modal.open({
          templateUrl: 'uploadFileModal.html',
          controller: 'UploadFileController',
          size: 'lg'
        });

        modalInstance.result.then(function(data){
            console.log('ok', data);
            fileUpload.uploadFileToUrl(data.uploadFile, data.project_name, '/odaweb/_upload').success(function(data){
                $scope.configureFile(data);
            });
        });
    };

    $scope.goToAddressPrompt = function() {
        var modalInstance = $modal.open({
          templateUrl: 'gotoAddressModal.html',
          controller: 'GotoAddressController',
          size: 'md'
        });

        modalInstance.result.then(function(data){
            console.log(data);
        });
    };

    $scope.$on('command.goto', function(event) {
        $scope.goToAddressPrompt();
    });

    $scope.$on('command.open', function(event) {
        $scope.openFile();
    });

    $scope.configureFile = function(fileData) {
        console.log(fileData);
        var modalInstance = $modal.open({
          templateUrl: 'configureFileModal.html',
          controller: 'ConfigureFileController',
          resolve: { fileData : function() {return fileData;} },
          size: 'lg'
        });

        modalInstance.result.then(function(data){
            console.log(data, fileData);
            window.location = "/oda/ace/" + fileData.short_name;
        });
    };

});

var UploadFileController = function($scope, $modalInstance){

    //http://stackoverflow.com/questions/18716113/scope-issue-in-angularjs-using-angularui-bootstrap-modal
    $scope.data = {
        projectName: null
    }

    $scope.ok = function () {
        $modalInstance.close({
            projectName: $scope.data.projectName,
            uploadFile: $scope.uploadFile
        });
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

};

var ConfigureFileController = function($scope, $modalInstance, fileData) {

    $scope.fileData = fileData;

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function () {
        $modalInstance.close({});
    };

    var arch = fileData.arch;
    $scope.optionsTemplate = function() {
        var view = '/odaweb/optionsview?arch=' + arch
        return view;
    };

};

var GotoAddressController = function($scope, $modalInstance, OdaSession) {
    $scope.data = {
        address: null
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function () {
        var position = parseInt($scope.data.address.substring(2),16);
        console.log('set position', position);
        OdaSession.getSession().moveToOffset(position);
        $modalInstance.close({address: $scope.data.address});
    };

}

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


odaApplication.factory('odaApi', function($rootScope, $q, $http) {

    var position = 0;
    oda_shortcuts = new window.keypress.Listener();

    return {
        getStrings : function(short_name, revision) {
            var deferred = $q.defer();
            return $http.get('/odaweb/api/strings/?short_name=' + short_name + "&revision=" + revision)
                .success(function(data, status) {
                // Some extra manipulation on data if you want...
                deferred.resolve(data);
            }).error(function(data, status) {
                deferred.reject(data);
            });

            return deferred.promise;
        },
        getSections : function(short_name, revision) {
            return $http.get('/odaweb/api/sections/', {
                params: {
                    short_name : short_name,
                    revision : revision
                },
                cache: true
            });
        },
        getDisplayUnits : function(short_name, revision, addr, quantity) {
            return $http.get('/odaweb/api/displayunits/?', {
                params: {
                    short_name : short_name,
                    revision : revision,
                    addr : addr,
                    units : quantity
                }/*,
                cache: true*/
            });
        },
        getSymbols : function(short_name, revision) {
            return $http.get('/odaweb/api/symbols/?short_name=' + short_name + "&revision=" + revision);
        },
        getComments : function(short_name, revision) {
            return $http.get('/odaweb/api/comments/?short_name=' + short_name + "&revision=" + revision);
        },
        getFunctions : function(short_name, revision) {
            console.debug('getting functions for ' + short_name + ' revision ' + revision);
            return $http.get('/odaweb/api/functions/', {
                params: {
                    short_name : short_name,
                    revision : revision
                }
            });
        },
        setLabel : function(id, label) {
            return $http({
                method: 'PATCH',
                url: '/odaweb/api/labels/'+id+"/",
                data: {
                  label: label
                }
            });
        },
        setOdaOptions: function(id, target, arch) {
            return $http({
                method: 'PATCH',
                url: '/odaweb/api/odaoptions/'+id+"/",
                data: {
                  target: target,
                  architecture: arch
                }
            });
        },
        setComment : function(id, comment) {
            return $http({
                method: 'PATCH',
                url: '/odaweb/api/comments/'+id+"/",
                data: {
                  comment: comment
                }
            });
        },
        getLabels : function(short_name, revision) {
            return $http.get('/odaweb/api/labels/', {
                params: {
                    short_name : short_name,
                    revision : revision
                }
            });
        },
        getPosition: function() {
            return postion;
        },
        setPosition: function(newPosition) {
            if (position != newPosition) {
                console.log("setting new position to " + newPosition.toString(16));
                position = newPosition;
                $rootScope.$broadcast("position", position);
            }
        },
        setLiveEntryText: function(liveEntryText) {
            var deferred = $q.defer();

            $http({
                method: 'PATCH',
                url: '/odaweb/api/binarystrings/'+oda_util.getMaster().binary.id+"/",
                data: {
                  binary_string: liveEntryText.replace(/\s/g, ''),
                  short_name: oda_util.getMaster().short_name,
                  revision: oda_util.getMaster().revision
                }
            }).success(function(data){
                $rootScope.$broadcast("liveEntryText", position);
                deferred.resolve(data);
            }).error(function(){
                deferred.reject("Use only hex characters!");
            });
            return deferred.promise;
        },
        updatePlatformOptions: function(options) {
             $rootScope.$broadcast("liveEntryText", position);
             $rootScope.$broadcast("platformOptionsChanged", options);
        },
        find : function(short_name, revision, bytes) {
            return $http.get('/odaweb/api/find/?short_name=' + short_name + "&revision=" + revision + "&bytes=" + bytes);
        },
        shortcut : function(combo, func) {
            oda_shortcuts.simple_combo(combo, func, true);
        }
    };
});

