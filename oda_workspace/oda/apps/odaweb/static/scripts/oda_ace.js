var ace_document = ace.require('ace/document');

var OdaSession = function(session) {

    this.cursorPositon = null;

    this.onCursorChange = $.Callbacks();

    session.selection.on('changeCursor', function(e) {
        var cursor = session.getSelection().getCursor();
        var line = session.getDocument().getLine(cursor.row);

        try {
            var offset = JSON.parse(line).offset;
            this.onCursorChange.fire(offset);
        } catch (ex) {
        }

    }.bind(this));

};

var CommentDialog = function(editor, du) {
    var modalId = "#my-modal";
    var saveButtonId = "#my-modal .btn-primary";

    $('#my-modal .commentLine').text(du);
    $(modalId).unbind().on('shown.bs.modal', function (e) {
        // do something...
        $('#my-modal .comment-text').focus();
    });

    $(modalId).on('hidden.bs.modal', function (e) {
        editor.focus();
    });

    this.modal = $('#my-modal').modal('show');


    $(saveButtonId).unbind().on('click', function () {
        alert($('#my-modal .comment-text').val());
        this.modal.modal('hide');
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

Handlebars.registerHelper("hex", function(value){
    var stringValue = value.toString(16);
    var s = "000000000" + stringValue;
    return s.substr(s.length-8);

});


var KeyboardHandler = function(statusBar) {

    this.mode = 'normal';

    this.statusBar = statusBar;

    this.setMode = function(mode) {
        this.mode = mode;
        this.statusBar.setMode(mode);
    };

    this.normalMode = function(data, hashId, key, keyCode, e) {
        //Arrow Keys
        if (keyCode >=33 && keyCode <= 40 ) {
            return null;
        }

        var editor = data.editor;
        var session = editor.getSession();
        if (key == ';') {
            var cursor = session.getSelection().getCursor();
            var line = session.getDocument().getLine(cursor.row);

            var commentDialog = new CommentDialog(editor, line);
        }

        console.log("keyboard", data, hashId, key, keyCode, e);
        return {
            command: "null"
        };
    };

    this.virtual = new VirtualTextBox();
    this.commentMode = function(data, hashId, key, keyCode, e) {


        if (key == 'esc' || key == 'return') {
            this.setMode('normal');
        } else {
            this.virtual.processKey(key);
        }


        return {
            command: "null"
        };
    };

    this.handler = function(data, hashId, key, keyCode, e) {
        // ignore command keys (shift, ctrl etc.)
        if (hashId !== 0 && (!key || keyCode == -1))
            return null;

        if (this.mode == 'normal') {
            return this.normalMode(data, hashId, key, keyCode, e);
        } else if (this.mode == 'comment') {
            return this.commentMode(data, hashId, key, keyCode, e);
        }
    }.bind(this);
};


$(document).ready(function(){

    var functions = [];
    $.get('/odaweb/api/functions/', {
        short_name: 'mkdir',
        revision: 0
    }).done(function(data){
        for (var i=0; i<data.length; i++) {
            functions[data[i].offset] = data[i];
        }
    });

    var WindowLoader = function() {
        this.windowSize = 500;
        this.lineSizes = [];

        this.load = function(rowNum, callback) {
            var duNum = this.rowToDisplayUnit(rowNum);

            NProgress.start();

            console.log("Loading...",rowNum);
            $.get('/odaweb/api/displayunits/', {
                short_name: 'mkdir',
                revision: 0,
                addr: duNum,
                logical: true,
                units: 400
            }).done(function(data){
                var tlines = [];
                for (var i=0; i<data.length; i++) {

                    if (functions[data[i].offset]) {
                        console.log("FUNCTION", data[i], functions[data[i].offset]);
                        tlines.push("FUNCTION");
                    }

                    tlines.push(JSON.stringify(data[i]));
                }
                NProgress.done();
                callback(new ace_document.Window(rowNum, tlines), 0);

            });

/*            for (var i=rowNum; i<rowNum + this.windowSize; i++) {

                var line = '<div style="height:14px" class="ace_line"><span class="branchLines"> &nbsp;</span><span class="offset disassembly-cell">.interp:4194872</span><span class="raw disassembly-cell">2f</span><span class="instruction"><span class="string">/</span></span></div>'
                var s = {"section_name":".text","offset":4233570,"rawBytes":"4889c7","instStr":"mov    rdi,rax","branch":"&#x2001;&#x2001;&nbsp;","branch_label":"&#x2001;&#x2001;&nbsp;","opcode":"mov","operands":"rdi,rax","stringRef":null,"branchRef":null,"targetRef":null,"crossRef":[],"isBranch":false,"isFunction":false,"labelName":"abc"}

            }*/


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
                    linesAdded += this.lineSizes[key];
                }
            }
            return row + linesAdded;
        };

        this.getWindowSize = function() {
            return this.windowSize;
        }
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

        if (line == "..") {
            stringBuilder.push(line);
        } else {
        try {
            var s = JSON.parse(line);

            var t = '<span class="branchLines">{{{branch}}}</span><span class="offset disassembly-cell">{{section_name}}:{{hex offset}}</span>' +
                '<span class="raw disassembly-cell">{{rawBytes}}</span><span class="instruction">{{{instStr}}}</span>';
            var template = Handlebars.compile(t);
            var renderedText = template(s)
            stringBuilder.push(renderedText);
        } catch(e) {
            stringBuilder.push('<span>' + line + '</span>');
            console.log(e);
        }
        }
        stringBuilder.push("</div>");

    };

    var addrBar;
    var editor;
    $.get('http://localhost:8000/odaweb/api/sections/?format=json&short_name=mkdir&revision=0').done(function(sections){
        addrBar = new AddressNavBar('#addr-bar-canvas', sections);
        addrBar.onChange(function(address) {
            $.get('/odaweb/api/displayunits/1/vmaToLda', {
                short_name: 'mkdir',
                revision: 0,
                vma: address
            }).done(function(ldu){
                editor.moveCursorToPosition({row:ldu,column:0});
            });
            console.log('My change handler: ' + address.toString(16));
        });
    });

    $.get('/odaweb/api/displayunits/1/size', {
        short_name: 'mkdir',
        revision: 0
    }).done(function(data){
            var doc = new ace_document.OnlineDocument(data, new WindowLoader());
            doc.setLoadingString("..");
            editor = ace.edit("editor", doc);
            editor.setTheme("ace/theme/chrome");
            editor.setLineRenderer(lineRenderer);
            editor.getSession().setMode("ace/mode/javascript");
            editor.getSession().setUseWorker(false);
            editor.setShowPrintMargin(false);
            editor.renderer.setShowGutter(false);
            var odaSession = new OdaSession(editor.getSession());
            var statusBar = new StatusBar();
            var keyboardHandler = new KeyboardHandler(statusBar);

            odaSession.onCursorChange.add(function(offset) {
                console.log("CURSOR CHANGE", offset);
                addrBar.setAddress(offset);
                statusBar.setAddress(offset);
            })

            editor.setKeyboardHandler(keyboardHandler.handler);
    });



});