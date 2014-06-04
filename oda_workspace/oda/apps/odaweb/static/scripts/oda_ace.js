$(document).ready(function(){

    var document = ace.require('ace/document');

    var WindowLoader = function() {
        this.windowSize = 500;

        this.load = function(rowNum, callback) {

            NProgress.start();

            console.log("Loading...",rowNum);
            $.get('/odaweb/api/displayunits/', {
                short_name: 'chown',
                revision: 0,
                addr: rowNum,
                logical: true,
                units: 500
            }).done(function(data){
                var tlines = [];
                for (var i=0; i<data.length; i++) {
                    tlines.push(JSON.stringify(data[i]));
                }
                NProgress.done();
                callback(new document.Window(rowNum, tlines));

            });

/*            for (var i=rowNum; i<rowNum + this.windowSize; i++) {

                var line = '<div style="height:14px" class="ace_line"><span class="branchLines"> &nbsp;</span><span class="offset disassembly-cell">.interp:4194872</span><span class="raw disassembly-cell">2f</span><span class="instruction"><span class="string">/</span></span></div>'
                var s = {"section_name":".text","offset":4233570,"rawBytes":"4889c7","instStr":"mov    rdi,rax","branch":"&#x2001;&#x2001;&nbsp;","branch_label":"&#x2001;&#x2001;&nbsp;","opcode":"mov","operands":"rdi,rax","stringRef":null,"branchRef":null,"targetRef":null,"crossRef":[],"isBranch":false,"isFunction":false,"labelName":"abc"}

            }*/


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
                        this.config.lineHeight * (
                        this.$useLineGroups() ? 1 :this.session.getRowLength(row)
                        ), "px'>"
        );

        if (line == "..") {
            stringBuilder.push(line);
        } else {
        try {
            var s = JSON.parse(line);
            var t = '<span class="branchLines">{{{branch}}}</span><span class="offset disassembly-cell">{{section_name}}:{{offset}}</span>' +
                '<span class="raw disassembly-cell">{{rawBytes}}</span><span class="instruction">{{{instStr}}}</span>';
            var template = Handlebars.compile(t);
            var renderedText = template(s)
            stringBuilder.push(renderedText);
        } catch(e) {
            console.log(e);
        }
        }
        stringBuilder.push("</div>");

    };

    var doc = new document.OnlineDocument(80000, new WindowLoader());
    doc.setLoadingString("..");
    var editor = ace.edit("editor", doc);
    editor.setTheme("ace/theme/chrome");
    editor.setLineRenderer(lineRenderer);
    editor.getSession().setMode("ace/mode/javascript");
    editor.getSession().setUseWorker(false);
    editor.setShowPrintMargin(false);

});