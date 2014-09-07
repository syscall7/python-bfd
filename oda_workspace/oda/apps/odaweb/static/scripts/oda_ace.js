"use strict";

var ace_document = ace.require('ace/document');
var oop = ace.require("ace/lib/oop");
var EventEmitter = ace.require("ace/lib/event_emitter").EventEmitter;

var OdbFile = function(oda_master) {

    this.oda_master = oda_master;

    this.binary = oda_master.binary;

    this.functions = [];

    this.sections = [];

    this.parcels = [];

    this.comments = [];

    this.symbols = [];

    this.displayUnitsLength = -1;

    this.shortName = null;

    this.revision = 0;

    this.strings = [];


    this.load = function () {
        this.shortName = this.oda_master.short_name;

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

        var cmq = $.get('/odaweb/api/comments/', {
            short_name: this.shortName,
            revision: 0
        }).success(function(data){
            for (var i=0; i<data.length; i++) {
                this.comments[data[i].offset] = data[i];
            }
        }.bind(this));

        var dulenq = $.get('/odaweb/api/displayunits/1/size', {
            short_name: this.shortName,
            revision: 0
        }).success(function (data) {
            this.displayUnitsLength = data;
        }.bind(this));

        var symq = $.get('/odaweb/api/symbols/', {
            short_name: this.shortName,
            revision: 0
        }).success(function(data) {
            this.symbols = data;
        }.bind(this));

        var stringsq = $.get('/odaweb/api/strings/', {
            short_name: this.shortName,
            revision: 0
        }).success(function(data) {
            this.strings = data;
        }.bind(this));

        $.when(fq, sq, pq, symq, stringsq, dulenq, cmq).done(function (data) {
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

        $.post("/odaweb/api/comments/",{
            short_name: this.shortName,
            revision: 0,
            comment: comment,
            offset: offset
        }).success(function(data){
            this.comments[offset] = {
                comment: comment,
                offset: offset
            };


            this._signal('changed', {
                addr: offset,
                action: 'insertComment'
            });
        }.bind(this));
    };

    this.setOptions = function(options){
        $.ajax({
            url: '/odaweb/api/options/'+this.binary.id+"/",
            type: 'PATCH',
            data: {
                options: options,
                short_name: this.shortName,
                revision: this.revision
            }
        }).success(function(data) {
            console.log(data);
            this._signal('liveEntryText', {
                addr: 0,
                action: 'liveEntryChanged'
            });

        }.bind(this));
    };

    this.setLiveEntryText = function(liveEntryText) {
        $.ajax({
            url: '/odaweb/api/binarystrings/'+this.binary.id+"/",
            type: 'PATCH',
            data: {
                binary_string: liveEntryText.replace(/\s/g, ''),
                short_name: this.shortName,
                revision: this.revision
            }
        }).success(function() {
            this._signal('liveEntryText', {
                addr: 0,
                action: 'liveEntryChanged'
            });
        }.bind(this));

        /*
        var deferred = $q.defer();

        $http({
            method: 'PATCH',
            url: '/odaweb/api/binarystrings/'+this.binary.id+"/",
            data: {

            }
        }).success(function(data){
            this._signal('liveEntryText', { });
            deferred.resolve(data);
        }.bind(this)).error(function(){
            deferred.reject("Use only hex characters!");
        });
        return deferred.promise;*/
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

    this.lastOffset = null;

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
            if (offset != this.lastOffset) {
                this.lastOffset = offset;
                this._signal('cursor.change', {
                    offset: offset
                });
            }
            //this.onCursorChange.fire(offset);
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
    .module('odaApp',['ngSanitize', 'ui.bootstrap', 'ui.keypress'])
    .config(function($httpProvider) {

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

});

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
    editor.setTheme("ace/theme/chrome");
    editor.setLineRenderer(lineRenderer);
    editor.getSession().setMode("ace/mode/javascript");
    editor.getSession().setMode(new OdaMode());
    editor.getSession().setUseWorker(false);
    editor.setShowPrintMargin(false);
    editor.renderer.setShowGutter(true);

    var odaSession = new OdaSession(editor, odbFile, windowLoader);
    var statusBar = new StatusBar();

    windowLoader.session = editor.getSession();
    editor.getSession().gutterRenderer = new OdaGutterRenderer(odaSession);


    odaSession.on('cursor.change', function(e) {
        var offset = e.offset;
        console.log("CURSOR CHANGE", offset);
        addrBar.setAddress(offset);
        statusBar.setAddress(offset);
    })



    odbFile.on('changed', function(e){
        console.log("odbFile.on('changed')", e);
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

    odaApplication.value('odbFile', odbFile);
    odaApplication.value('editor', editor);
    odaApplication.value('odaSession', odaSession);

    //Keyboard Handling
    odaApplication.run(function($rootScope){
        editor.setKeyboardHandler(function(data, hashId, key, keyCode, e) {
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
        });
    });

    //Socket IO
    odaApplication.run(function($rootScope){
        var socket = io.connect("http://" + window.location.hostname + ":8080", {
            reconnection: false
        });

        socket.on('join', function(data) {
            console.log('join', data);
            addrBar.addUser(data.username);
            addrBar.updateUser(data.username, 0x403000);
        });

        socket.emit('subscribe',{
            //todo username
            username: 'USERNAME',
            room: odbFile.shortName
        });


        socket.on('cursor.change', function(e){
            addrBar.updateUser(e.username, e.offset);
        });

        odaSession.on('cursor.change', function(e){
            socket.emit('cursor.change',{
                offset: e.offset
            });
        });

    });


    angular.bootstrap(document, ['odaApp']);

}

odaApplication.run(function($rootScope, $modal, odbFile){
    $rootScope.$on('command.comment', function(event, line){

        var scope = $rootScope.$new(true);
        scope.line = line;

        console.log("LINE", line);
        var modalInstance = $modal.open({
          templateUrl: 'commentModal.html',
          controller: 'CommentController',
          size: 'lg',
          scope: scope
        });

        modalInstance.opened.then(function(){
            setTimeout(function() { $('.comment-text').focus(); }, 100);
        });

        modalInstance.result.then(function(data){
            odbFile.addComment(line.line.data.offset, data.comment);
        });

    });
});

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

odaApplication.run(function($rootScope, Docker, odbFile, odaSession, editor){
    odbFile.on('liveEntryText', function(event, liveEntryText) {
        //var odaSession = oda_util.getOdaSession();
        //var odbFile = oda_util.getOdbFile();
        if (odaSession != null && odbFile != null) {
            //We have to get the new size here since the number of DUs could possibly have changed
            odbFile.duLength(function(length){
                editor.getSession().getDocument().setLength(length);
                odaSession.windowLoader.reload(true)
            });


        }
    });

    //http://dmauro.github.io/Keypress/
    var listener = new window.keypress.Listener($('.theeditor')[0]);


    listener.simple_combo("ctrl g", function() {
        console.log("You pressed ctrl g");
        //todo activate textbox
        $rootScope.$broadcast('command.goto');
    });

    listener.simple_combo(';', function(){
        var session = editor.getSession();

        var cursor = session.getSelection().getCursor();
        var line = session.getDocument().getLineData(cursor.row);


        $rootScope.$broadcast('command.comment', {
            line: line
        });
    });

    listener.simple_combo('c', function(){
        var session = editor.getSession();

        var cursor = session.getSelection().getCursor();
        var line = session.getDocument().getLineData(cursor.row);

        odbFile.makeCode(line.data.offset, function(data){
            odaSession.windowLoader.reload();
        });
    });

    listener.simple_combo('d', function(){
        var session = editor.getSession();

        var cursor = session.getSelection().getCursor();
        var line = session.getDocument().getLineData(cursor.row);

        odbFile.makeData(line.data.offset, function(data){
            odaSession.windowLoader.reload();
        });
    });

    listener.simple_combo("ctrl u", function(){
        $rootScope.$broadcast('command.open');
    });

    listener.simple_combo("ctrl f", function(){
        $rootScope.$apply(function(){Docker.select(Docker.docks[2]);});
    });
});

$(document).ready(function(){
    $.ajaxSetup({
        headers: { "X-CSRFToken": $.cookie("csrftoken") }
    });

    var top = parseInt($('.theeditor').css('top'));
    var bottom = parseInt($('.theeditor').css('bottom'));
    $('#editor').height($(window).height()-top-bottom - 5);
    $(window).resize(function(){
        $('#editor').height($(window).height()-top-bottom - 5 );
    });


    var odbFile = new OdbFile(window.oda_master);

    odbFile.load();

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

    context.init({preventDoubleContext: false});
	context.attach('#editor', [

		{header: 'Download'},
		{text: 'The Script', subMenu: [
			{header: 'Requires jQuery'},
			{text: 'context.js', action: function(e){
				alert('here');
			}}
		]},
		/*{text: 'The Styles', subMenu: [

			{text: 'context.bootstrap.css', href: 'http://lab.jakiestfu.com/contextjs/context.bootstrap.css', target:'_blank', action: function(e){
				_gaq.push(['_trackEvent', 'ContextJS Bootstrap CSS Download', this.pathname, this.innerHTML]);
			}},

			{text: 'context.standalone.css', href: 'http://lab.jakiestfu.com/contextjs/context.standalone.css', target:'_blank', action: function(e){
				_gaq.push(['_trackEvent', 'ContextJS Standalone CSS Download', this.pathname, this.innerHTML]);
			}}
		]},*/
		{divider: true},
		{header: 'Meta'},
		{text: 'The Author', subMenu: [
			{header: '@jakiestfu'},
			{text: 'Website', href: 'http://jakiestfu.com/', target: '_blank'},
			{text: 'Forrst', href: 'http://forrst.com/people/jakiestfu', target: '_blank'},
			{text: 'Twitter', href: 'http://twitter.com/jakiestfu', target: '_blank'},
			{text: 'Donate?', action: function(e){
				e.preventDefault();
				$('#donate').submit();
			}}
		]},
		/*{text: 'Hmm?', subMenu: [
			{header: 'Well, thats lovely.'},
			{text: '2nd Level', subMenu: [
				{header: 'You like?'},
				{text: '3rd Level!?', subMenu: [
					{header: 'Of course you do'},
					{text: 'MENUCEPTION', subMenu: [
						{header:'FUCK'},
						{text: 'MAKE IT STOP!', subMenu: [
							{header: 'NEVAH!'},
							{text: 'Shieeet', subMenu: [
								{header: 'WIN'},
								{text: 'Dont Click Me', href: 'http://bit.ly/1dH1Zh1', target:'_blank', action: function(){
									_gaq.push(['_trackEvent', 'ContextJS Weezy Click', this.pathname, this.innerHTML]);
								}}
							]}
						]}
					]}
				]}
			]}
		]}*/
	]);


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

odaApplication.service('CursorPosition', function(){

});

odaApplication.service('Docker', function(odbFile) {
    var master = odbFile.oda_master;

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

odaApplication.controller('NavbarController', function NavbarController($scope, $modal, $location, fileUpload, AuthService){
    $scope.examples = window.examples;


    $scope.credentials = {
        username: '',
        password: ''
    };

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
                window.location = "/oda/ace/" + fileData.short_name;
            }
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

var MonitorSandboxController = function($scope, $interval, $http, fileInfo) {
    var checking;

    $http.post('/odaweb/api/sandbox', {
        short_name: fileInfo.shortName,
        revision: fileInfo.revision
    }).success(function(job){
        checking = $interval(function(){
            console.log('checking...');

            $http.get('/odaweb/api/sandbox', {
                params: {
                    job_id: job.job_id
                }
            }).success(function(job_status) {
                $scope.job_status = job_status.status['msg']
            });
        }, 3000);
    });


};

var ConfigureFileController = function($scope, $modalInstance, fileData) {

    console.log(fileData);

    $scope.data = {
        fileData: fileData,
        sandbox: false
    }

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function () {
        $modalInstance.close({
            sandbox: $scope.data.sandbox,
            shortName: fileData.short_name,
            revision: fileData.revision

        });
    };

    var arch = fileData.arch;
    $scope.optionsTemplate = function() {
        var view = '/odaweb/optionsview?arch=' + arch
        return view;
    };

    $scope.options = {
        architecture: fileData.arch
    };
    $scope.optionsUpdated = function() {
        console.log($scope.options);
    };

};

var GotoAddressController = function($scope, $modalInstance, odaSession) {
    $scope.data = {
        address: null
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function () {
        var position = parseInt($scope.data.address.substring(2),16);
        console.log('set position', position);
        odaSession.moveToOffset(position);
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
        }
    };
});

odaApplication.run(function($rootScope, AuthService){
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
