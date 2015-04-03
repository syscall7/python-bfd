var intToHex = function(value){
    var stringValue = value.toString(16);
    var s = "000000000" + stringValue;
    return s.substr(s.length-8);

};

$(document).ready(function(){
    Handlebars.registerHelper("hex", intToHex);

    Handlebars.registerHelper("pad", function(value, length) {
        var counter = length - value.length;
        for(var i=0; i<counter; i++) {
            value = value.concat("&nbsp;");
        }
        return value;
    });
});

(function($) {
    function Renderer(odbFile) {

        function cloneDu(du) {
            var clonedDu = $.extend({}, du);
            return clonedDu;
        }

        function createDuFactory(du) {
            return function(instStr) {
                var cloned = cloneDu(du);
                cloned.instStr = instStr;

                cloned.branch = '';

                if (instStr == "") {
                    cloned.rawBytes = "";
                }
                return cloned;
            };
        }

        this.functionTemplate1 = Handlebars.compile(
            '<span class="instruction">; =============== F U N C T I O N ====================================</span>');

        this.functionTemplate2 = Handlebars.compile(
            '<span class="oda-editable function-params function-return" data-function-addr="{{offset}}" data-function-field="retval" contenteditable="true">{{retval}}</span> ' +
            '<span class="oda-editable function-params function-name "  data-function-addr="{{offset}}" data-function-field="name"  contenteditable="true">{{name}}</span> ' +
            '<span class="oda-editable function-params function-args"   data-function-addr="{{offset}}" data-function-field="params" contenteditable="true">({{args}})</span> ');

        this.labelTemplate = Handlebars.compile("{{{ pad '' 5}}} loc_{{ hex offset }}:");

        this.commentTemplate = Handlebars.compile('<span style="padding-left: 50px"><span contenteditable="true" data-addr={{offset}}" ' +
        'class="oda-editable comment">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></span>');

        this.commentTemplate2 = Handlebars.compile('<span style="padding-left: 50px">;<span contenteditable="true" data-addr={{offset}}" ' +
        'class="oda-editable comment">{{comment}}</span></span>');

        this.renderFunction = function(du, func) {
            //console.log('renderFunction', func);
            var createDu = createDuFactory(du);

            var theLines = [
                createDu(""),
                createDu(this.functionTemplate1(du))
            ];
            for (var i=0;i<du.crossRef.length; i++) {
                theLines.push(createDu('; CODE XREF:<span href="" class="xref-location" data-addr="' +
                    du.crossRef[i].offset + '">0x' + intToHex(du.crossRef[i].offset) + '</span>'));
            }
            theLines.push(createDu(""));
            theLines.push(createDu(this.functionTemplate2($.extend({}, du, func))));
            theLines.push(createDu(""));
            return theLines;
        };

        this.renderBranch = function(du) {
            //console.log('renderBranch');
            var createDu = createDuFactory(du);

            return [createDu(""), createDu(this.labelTemplate(du)), createDu(du.instStr)]
        };

        this.renderTarget = function(du) {
            var createDu = createDuFactory(du);

            var label = '<span href="" data-addr="' + du.targetRef.offset + '" class="xref-location"> loc_' + du.targetRef.offset.toString(16) + '</span>';

            if (odbFile.functions[du.targetRef.offset]) {
                    label =  '<span href="" data-addr="' + du.targetRef.offset + '" class="xref-location">' + odbFile.functions[du.targetRef.offset].name + "</span>";
            } else if (odbFile.labels[du.targetRef.offset]) {
                label =  '<span href="" data-addr="' + du.targetRef.offset + '" class="xref-location">' + odbFile.labels[du.targetRef.offset].name + "</span>";
            }

            return [createDu(du.instStr + label)]
        };

        this.render = function(dus) {
            var rowCounter = 0;

            var data = [];

            for (var i = 0; i < dus.length; i++) {
                var instr = dus[i];

               if (odbFile.functions[instr.offset]) {
                    var funcLines = this.renderFunction(instr, odbFile.functions[instr.offset]);
                    data.push.apply(data, funcLines)
                    rowCounter += funcLines.length;
                }

                if (instr.isBranch) {
                    var branchDus = this.renderBranch(instr);
                    data.push.apply(data, branchDus);
                    rowCounter += branchDus.length;
                }
                if (instr.targetRef) {
                    var targetRender = this.renderTarget(instr);
                    data.push.apply(data, targetRender);
                    rowCounter += targetRender.length;
                }
                else {
                    var comment = odbFile.comments[instr.offset];
                    var renderedComment = this.commentTemplate({offset: instr.offset});
                    if (comment) {
                        console.log("comment", comment);
                        renderedComment = this.commentTemplate2({offset: instr.offset, comment: comment.comment})
                    }
                    instr.instStr += renderedComment;
                    data[rowCounter] = instr;
                    rowCounter += 1;
                }


            }

            return data;
        };

        this.indexRows = function(data, from) {
            console.log("indexRows", from);
            for (var i=0;i<data.length; i++) {
                data[i].index = from + i;
            }
        };
    }

    $.extend(true, window, {Oda: {Renderer: Renderer}});
})(jQuery);

(function ($) {
    /***
     * A sample AJAX data store implementation.
     * Right now, it's hooked up to load all Apple-related Hackernews stories, but can
     * easily be extended to support and JSONP-compatible backend that accepts paging parameters.
     */
    function RemoteModel(odbFile) {

        // private
        var PAGESIZE = 400; // if this is too big, API will generate 400 errors
        var data = {length: 0};
        var searchstr = "apple";

        // events
        var onDataLoading = new Slick.Event();
        var onDataLoaded = new Slick.Event();
        var onDataCleared = new Slick.Event();

        var isProcessing = false;

        var first = null;
        var last = null;

        var renderer = new Oda.Renderer(odbFile);

        function init() {
        }


        function isDataLoaded(from, to) {
            for (var i = from; i <= to; i++) {
                if (!data[i] || data[i] == null) {
                    return false;
                }
            }

            return true;
        }

        function clear() {
            for (var key in data) {
                delete data[key];
            }
            data.length = 0;

            first = null;
            last = null;
            onDataCleared.notify();
        }

        function inLoadedRange(num) {
            if (first == null || last == null) {
                return false;
            }
            if (num > first && num < last) {
                return true;
            }
            return false;
        }

        function ajaxEnsureData(from, to) {
            //console.log('ensuredata', from, to);

            if (isProcessing || isDataLoaded(Math.max(0,from - 75), to + 125)) {
                return;
            }

            isProcessing = true;
            console.log('ajaxEnsureData', from, to);
            var startRow = Math.max(0, from - 150 );
            var numRows = PAGESIZE;
            var pivot = (from >= 150 ? 150 : from);

            console.log(" Math.abs(startRow - last)",  first, last, startRow);
            if (inLoadedRange(startRow)) {

                var offset = data[last - 1].offset;
                console.log('append: ', offset.toString(16));

                $.get('/odaweb/api/displayunits/', {
                    short_name: odbFile.shortName,
                    revision: odbFile.revision,
                    addr: offset,
                    units: numRows
                }).success(onSuccessAppend)
                    .error(function () {
                        onError(fromPage)
                    }).then(function(){isProcessing=false;});

            } else if (inLoadedRange(startRow + numRows)) {
                /*TODO: This needs to be adjusted by start - (additional lines)
                    the problem is that after we've rendered the lines it may have
                    accidentally rewritten some lines after the range, we means we
                    need to adjust the start
                */
                console.log("append-beginning: THIS NEEDS TO BE FIXED UP");
                $.ajax("http://localhost:8080/instructions", {
                    cache: true,
                    data: {start: startRow, num: numRows}
                }).success(onSuccess)
                    .error(function () {
                        onError(fromPage)
                    }).then(function(){isProcessing=false;});
            } else {
                clear();
                console.log("getting", startRow, numRows);
                $.get('/odaweb/api/displayunits/', {
                    short_name: odbFile.shortName,
                    revision: odbFile.revision,
                    addr: startRow,
                    logical: true,
                    units: numRows
                }).success(function(data) {
                    onSuccess(data, startRow, pivot);
                }).error(function () {
                        onError(fromPage)
                    }).then(function(){isProcessing=false;});
            }

            onDataLoading.notify();
        }

        var ensureData = _.debounce(ajaxEnsureData, 250);

        function onError(fromPage) {
            i = indicators.pop();
            if (i != null)
                i.fadeOut();
            alert("error loading page " + fromPage);
        }

        function onSuccess(resp, start, pivot) {
            console.log("Start: " + start + " Pivot:" + pivot);

            var beforeBlock = resp.slice(0, pivot);
            var afterBlock = resp.slice(pivot);

            var from = start + pivot;

            data.length = 30000; //Math.min(parseInt(resp.hits)); // limitation of the API

            var renderedRows = renderer.render(afterBlock);
            renderer.indexRows(renderedRows, from);
            for (var i=0; i<renderedRows.length; i++) {
                data[from + i] = renderedRows[i];
            }

            var to = from + renderedRows.length;

            if (last == null || last < (renderedRows.length + from)) {
                last = renderedRows.length + from;
                console.log("Setting last", last);
            }

            var beforeRenderedRows = renderer.render(beforeBlock);
            renderer.indexRows(beforeRenderedRows, from - beforeRenderedRows.length);
            for (var i=0; i<beforeRenderedRows.length; i++) {
                data[from - i - 1] = beforeRenderedRows[beforeRenderedRows.length - i - 1];
            }
            if (first == null || first > from-beforeRenderedRows.length) {
                first = from-beforeRenderedRows.length;
                console.log("setting first", first);
            }

            onDataLoaded.notify({from: from, to: to});
        }

        function onSuccessAppend(resp) {
            var from = last - 1;
            //data.length = Math.min(parseInt(resp.hits)); // limitation of the API

            if (first == null || first > from) {
                first = from;
                console.log("setting first", first);
            }

            var renderedRows = renderer.render(resp);
            renderer.indexRows(renderedRows, from);
            for (var i=0; i<renderedRows.length; i++) {
                data[from + i] = renderedRows[i];
            }

            var to = from + renderedRows.length;

            if (last == null || last < (renderedRows.length + from)) {
                last = renderedRows.length + from;
                console.log("Setting last", last);
            }

            onDataLoaded.notify({from: from, to: to});
        }


        function reloadData(from, to) {
            for (var i = from; i <= to; i++)
                delete data[i];

            ensureData(from, to);
        }


        function setSearch(str) {
            searchstr = str;
            clear();
        }


        init();

        return {
            // properties
            "data": data,

            // methods
            "clear": clear,
            "isDataLoaded": isDataLoaded,
            "ensureData": ensureData,
            "reloadData": reloadData,
            "setSearch": setSearch,

            // events
            "onDataLoading": onDataLoading,
            "onDataLoaded": onDataLoaded,
            "onDataCleared": onDataCleared
        };
    }

    // Slick.Data.RemoteModel
    $.extend(true, window, {Slick: {Data: {RemoteModel: RemoteModel}}});
})(jQuery);
