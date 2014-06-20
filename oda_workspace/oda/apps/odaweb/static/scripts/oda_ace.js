var ace_document = ace.require('ace/document');

var OdbFile = function() {

    this.functions = [];

    this.sections = [];

    this.displayUnitsLength = -1;


    this.load = function(shortName) {
        var fq = $.get('/odaweb/api/functions/', {
            short_name: 'mkdir',
            revision: 0
        }).success(function(data){
            for (var i=0; i<data.length; i++) {
                this.functions[data[i].offset] = data[i];
            }
        }.bind(this));

        var sq = $.get('/odaweb/api/sections/', {
            short_name: 'mkdir',
            revision: 0
        }).success(function(data){
            this.sections = data;
        }.bind(this));

        var dulenq = $.get('/odaweb/api/displayunits/1/size', {
            short_name: 'mkdir',
            revision: 0
        }).success(function(data) {
            this.displayUnitsLength = data;
        }.bind(this));

        $.when(fq, sq, dulenq).done(function(data) {
            this._signal('loaded', this);
        }.bind(this));
    };

    this.loadDu = function(addr, numUnits, callback) {
        $.get('/odaweb/api/displayunits/', {
            short_name: 'mkdir',
            revision: 0,
            addr: addr,
            logical: true,
            units: numUnits
        }).done(callback);
    };

    this.vmaToLda = function(vma, callback) {
        $.get('/odaweb/api/displayunits/1/vmaToLda', {
            short_name: 'mkdir',
            revision: 0,
            vma: vma
        }).done(callback);
    };

    this.makeData = function(vma, callback) {
        $.get('/odaweb/api/displayunits/1/makeData', {
                    short_name: 'mkdir',
                    revision: 0,
                    vma: vma
        }).success(callback)
    };

    this.callbacks = {};
    this.on = function(name, handler) {
        if (!this.callbacks[name]) {
            this.callbacks[name] = $.Callbacks();
        }
        this.callbacks[name].add(handler);

    };
    this._signal = function(name, data) {
        if (!this.callbacks[name]) {
            this.callbacks[name] = $.Callbacks();
        }
        this.callbacks[name].fire(data);
    };

}

var OdaSession = function(session, windowLoader) {

    //this.cursorPositon = null;

    this.windowLoader = windowLoader;

    this.onCursorChange = $.Callbacks();

    session.selection.on('changeCursor', function(e) {
        var cursor = session.getSelection().getCursor();

        //var line = session.getDocument().getLine(cursor.row);
        var lineData = session.getDocument().getLineData(cursor.row);
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
        return session.getDocument().getLineData(row);
    };

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

    this.modal = $('#my-modal').modal('show');


    $(saveButtonId).unbind().on('click', function () {
        this.modal.modal('hide');
        this.closeHandler.fire(true);
    }.bind(this));



}

function string_insert(original, index, string) {
  if (index > 0)
    return original.substring(0, index) + string + original.substring(index, this.length);
  else
    return string + original;
};

var VirtualTextBox = function() {
    this.text = '';
    this.position = 0;

    this.processKey = function(key) {
        this.text = string_insert(this.text, this.position, key);
        console.log(this.text);
    }

    this.getText = function() {
        return this.text;
    };
}

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
}

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

                commentDialog.closeHandler.add(function (save) {
                    if (save) {
                        alert($('#my-modal .comment-text').val());
                    }

                    editor.focus();
                });

            }

            if (key == 'd') {

                console.log('d');
                this.odbFile.makeData(line.data.offset, function(data){
                    this.odaSession.windowLoader.reload();
                }.bind(this));

            }

        }
        console.log("keyboard", data, hashId, key, keyCode, e);
        return {
            command: "null"
        };

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

var Renderer = function(functions) {

    this.baseFunctionTemplateString =
       '{{duNum}}<span class="branchLines">{{{branch}}}</span><span class="offset">{{{formatSectionOffset section_name offset 15 }}}</span>&nbsp;&nbsp;' +
       '<span class="raw disassembly-cell">{{{pad " " 20}}}</span>&nbsp;&nbsp;';
    this.baseFunctionTemplate = Handlebars.compile(this.baseFunctionTemplateString);

    this.functionTemplate1 = Handlebars.compile(this.baseFunctionTemplateString +
        '<span class="instruction">=============== F U N C T I O N ====================================</span>');

    this.functionTemplate2 = Handlebars.compile(this.baseFunctionTemplateString +
        '<span class="function-return">{{retval}}</span> <span class="function-name">{{name}}</span> <span class="function-args">({{args}})</span>');


    this.baseDuTemplateString =
        '{{duNum}}<span class="branchLines">{{{branch}}}</span><span class="offset">{{{formatSectionOffset section_name offset 15 }}}</span>';
    this.baseDuTemplate = Handlebars.compile(this.baseDuTemplateString +
        '&nbsp;&nbsp;<span class="raw disassembly-cell">{{{pad rawBytes 20}}}</span>&nbsp;&nbsp;<span class="instruction">{{{instStr}}}</span>');
    this.labelTemplate = Handlebars.compile(this.baseDuTemplateString + "{{{ pad '' 20}}} loc_{{ hex offset }}");

    this.render = function(du) {

        if (functions[du.offset]) {
      //      console.log("FUNCTION", du, functions[du.offset]);
            var rendered_lines = this.renderFunction(du, functions[du.offset]);
            return rendered_lines;
        }

        return this.renderDu(du)

    };

    this.renderTargetRef = function(du) {
        var label = "0x" + du.targetRef.offset.toString(16);
        if (functions[du.targetRef.offset]) {
            label =  functions[du.targetRef.offset].name + '[<a href="" class="xref-location">0x' + intToHex(du.targetRef.offset) + '</a>]';
        }
        return label;
    };

    this.renderFunction =  function(du, func) {

        var theLines = [this.functionTemplate1(du)];
        for (var i=0;i<du.crossRef.length; i++) {
            theLines.push(this.baseFunctionTemplate(du) + '; CODE XREF:<a href="" class="xref-location">0x' + intToHex(du.crossRef[i].offset) + '</a>');
        }
        theLines.push(this.baseFunctionTemplate(du));
        theLines.push(this.functionTemplate2($.extend({}, du, func)));
        return theLines;
    }

    this.renderDu = function(du) {
        var renderedText = this.baseDuTemplate(du);
        if (du.isBranch) {
            return [this.labelTemplate(du), renderedText];
        } if (du.targetRef) {
            return [renderedText + this.renderTargetRef(du)]
        }
        else
            return [renderedText];
    };
};


var WindowLoader = function(renderer, odbFile) {
    this.windowSize = 500;
    this.lineSizes = [];
    this.renderer = renderer;
    this.odbFile = odbFile;


    this.callbacks = {};
    this.lastRowNumload;

    this.on = function(name, handler) {
        if (!this.callbacks[name]) {
            this.callbacks[name] = $.Callbacks();
        }
        this.callbacks[name].add(handler);

    };
    this._signal = function(name, data) {
        if (!this.callbacks[name]) {
            this.callbacks[name] = $.Callbacks();
        }
        this.callbacks[name].fire(data);
    };

    this.reload = function() {
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


            var addedLines = 0;

            for (var i=0; i<data.length; i++) {
                var renderedLines = this.renderer.render($.extend({},data[i], {duNum:i+duNum}));
                renderedLines = $.map(renderedLines, function(line) { return {row: line, data: data[i], num: i }});
                if (renderedLines.length != 1) {
                    if (!this.lineSizes[duNum+i])
                        addedLines += renderedLines.length;

                    this.lineSizes[duNum + i] = renderedLines.length;
                }

                tlines = tlines.concat(renderedLines);

            }
            NProgress.done();
            var currentWindow = new ace_document.Window(rowNum, tlines);
            this._signal("loaded", { window: currentWindow, additionalRows: addedLines });
           // callback(currentWindow, addedLines);

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
    }
};

function start(odbFile) {
    var editor;

    var renderer = new Renderer(odbFile.functions);
    var windowLoader = new WindowLoader(renderer, odbFile);

    var addrBar = new AddressNavBar('#addr-bar-canvas', odbFile.sections);

    addrBar.onChange(function(address) {
        odbFile.vmaToLda(address, function(ldu){
            editor.moveCursorToPosition({row:windowLoader.displayUnitToRow(ldu),column:0});
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
    var odaSession = new OdaSession(editor.getSession(), windowLoader);
    var statusBar = new StatusBar();
    var keyboardHandler = new KeyboardHandler(statusBar, odaSession, odbFile);

    odaSession.onCursorChange.add(function(offset) {
        console.log("CURSOR CHANGE", offset);
        addrBar.setAddress(offset);
        statusBar.setAddress(offset);
    })

    editor.setKeyboardHandler(keyboardHandler.handler);


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
            odbFile.vmaToLda(parseInt(xrefLocation[0].value.substring(2),16), function(ldu){
                editor.moveCursorTo(windowLoader.displayUnitToRow(ldu), 0);
                editor.clearSelection();
            });
        }


        return "null";
    });
}

$(document).ready(function(){
    var odbFile = new OdbFile();
    odbFile.load('mkdir');

    odbFile.on('loaded', function(odbFile){
        start(odbFile);
    });
});