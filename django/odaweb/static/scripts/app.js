var Binary = Backbone.Model.extend({

});

var Sidebar = Backbone.Model.extend({
    initialize : function() {

        $('.nav-btn').tooltip();
        $('.nav-btn').click(this, function(event){
            $('#sidebar .active').removeClass('active');
            $('.item').hide();
            $('#'+$(this).data('panel')).show();
            event.data.set('active_tab', $('#'+$(this).data('panel')).attr('id'));
        });

        $('#myTab a').click(function (e) {
            e.preventDefault();
            $(this).tab('show');
        });

        $('.item').hide();
        $('.active').show();
    },

    hideRaw : function() {
        $('#hex-display-btn').hide();
        $('#symbols-btn').click();
    },

    resize : function(elem) {
        var new_offset = $("#sidebarContent").offset().top;
        var accum_margins = 15; //Not captured by jquery
        if ( $(elem).find('table').length )
        {
            // Table header height
            new_offset += 36;
        }
        else
        {
            // Margins and Padding
            new_offset += 15;
        }
        new_offset += $("#sidebar").offset().top + accum_margins;
        return $(window).height()-new_offset;  //237;
    },

    close : function() {
        $("#close").click(function(){
            $('#sidebar').hide();
            $('#view').animate({
                left: '0'
            }, 250);
        });

        $("#show").click(function(){
            $('#sidebar').show();
            $('#view').animate({
                left: '400'
            }, 250);
        });
    }
});

var sidebar = new Sidebar();

function FileUploadTab() {
    $('#fileselectbutton').click(function(e){
        $('#file').trigger('click');
    });

    $('#file').change(function(e){
        var val = $(this).val();

        var file = val.split(/[\\/]/);

        $('#filename').val(file[file.length-1]);
    });

    $('#upload-submit-btn').click(function(e){
        $('#upload-form').submit();
    });
}

function ResizeHandler() {
    $(window).resize(function() {
        // TODO: Hardcoded Height includes footer and banner
        /*$('#view-container').height($(window).height()-74);*/
        $('#vertSplitter').height($(window).height()-47);
        
        // TODO: Hardcoded Height includes footer, banner, and tabs
        $('#myTabContent').height($(window).height()-132);
             
        $('.sidebar-scroll-container').each( function (i,elem) {
            $(elem).height( sidebar.resize($(elem)) );} );
        
    });
    //$('#view-container').height($(window).height()-74);
    $('#vertSplitter').height($(window).height()-47);
    $('#myTabContent').height($(window).height()-132);
    $('.sidebar-scroll-container').each( function (i,elem) {
        $(elem).height( sidebar.resize($(elem)) );} );

    
}

function InitializeSplitter() {
    $("#main-display").splitter({type: 'v'});    
}

/* ---------------------------------------------------------------------------------------------------------  *
 * ADDRESS SLIDER
 * ---------------------------------------------------------------------------------------------------------  */
function InitializeSlider(min, max) {

    var selectedRow = null;

    // remove border
    $(".ui-slider-horizontal").css('border', 0);
    $(".ui-slider-handle").removeClass('ui-corner-all');

    // set the slider address display text
    // NOTE: This function is triggered via updateSlider() in history.js as well
    function updateAddrDisplay(addr) {
        window.topDisplayAddr = addr;
        addrStr = addr.toString(16).toUpperCase();
        console.debug("updateAddrDisplay to %s", addrStr);
        while (addrStr.length < 8) addrStr = "0" + addrStr;
        $("#slider-address").text("0x" + addrStr);
    }

    // event handler for slider control
    function sliderHandler(addr) {

        // no need to set the slider position, that's already been done by the event
        updateAddrDisplay(addr);

        // Try to scroll to the address
        if ( !scrollToAddr(addr) )
        {
            // Isn't loaded. Try to load it
            //window.topDisplayAddr = addr;
            updateDisassembly(addr);
            scrollToAddr(addr);
        }
    }

    // setup slider
    $( "#slider" ).slider({
        change: function( event, ui ) { console.debug("slider change event"); updateAddrDisplay(ui.value); },
        slide: function( event, ui ) { console.debug("slider slide event"); updateAddrDisplay(ui.value); },
        stop: function( event, ui )  { console.debug("slider stop event"); sliderHandler(ui.value); },
        animate: true,
        min: min,
        max: max,
    });

    // set initial position
    updateAddrDisplay($("#slider").slider("value"));

    $(document).on("click", "#listing tr", function(){
        console.debug("selected row: " + $(this).attr('addr'));
        selectedRow = $(this);
        $('tr.selected').removeClass('selected');
        $(this).addClass('selected');
    });
    $(document).on("hover", "#listing tr", function(){
        updateAddrDisplay($(this).attr('addr'));
    });

    $("html").keypress(function(event) {
        if (String.fromCharCode(event.which) == 'g') {
            var strAddr = prompt("Go to address:");
            var addr = parseInt(strAddr, 16);
            console.debug("Setting slider to 0x%s", addr.toString(16));
            $("#slider").slider("value", addr );

            // Try to scroll to the address
            if ( !updateDisassembly(addr) )
            {
                // Isn't loaded. Try to load it
                scrollToAddr(addr);
            }
        } else if (String.fromCharCode(event.which) == ';') {
            if (selectedRow != null) {
                //console.debug('here');
                selectedRow.find('.comment').text('   ');
                selectedRow.find('.comment').focus();
            }
        }
    });

}

function SetupSectionFlagPopovers(sectionFlags) {

    // TODO: Move javascript from sections_tab.djhtml over to here

    /*
        $('.FLAG_{{flag.abbrev}}').popover({
            placement: 'bottom',
            delay: 0,
            title: '{{flag.name}}',
            content: '{{flag.desc}}',
        });
        */
}

function Load(binary) {

    window.DisChunkInfo = Backbone.Model.extend({});
    window.DisChunkList = Backbone.Collection.extend({
        model: window.DisChunkInfo
    });

    window.disChunks = new window.DisChunkList([]);
    window.disId = binary.id;

    var addr = 0;
    if (typeof window.initialOffset === "undefined")
    {
        addr = 0;
    }
    else
    {
        addr = window.initialOffset;
    }
    
    console.debug("Load, refreshDisassembly addr= %x %d %s",addr,addr,addr);    
    refreshDisassembly(addr);
    
    $.post('_symbols', {id: binary.id}).done(function(data){
        $('#symbol-content').append(data.symbols_html);
        scrolify($('#symbol-table')); // 160 is height
        ResizeHandler();
    }).fail(function(){
        alert('symbols fail to load');
    });

    $.post('_strings', {id: binary.id}).done(function(data){
        $('#strings-content').append(data.strings);
        scrolify($('#strings-table')); // 160 is height
        ResizeHandler();
    }).fail(function(){
            alert('symbols fail to load');
    });

    $.post('_sections', {id: binary.id}).done(function(data){

        $('#tab-sections').append(data.sections_tab);

        SetupSectionFlagPopovers(data.section_flags);

    }).fail(function(){
        alert('sections failed to load');
    });

    $.post('_fileinfo', {id: binary.id}).done(function(data){

        $('#tab-fileinfo').append(data.fileinfo_tab);

    }).fail(function(){
        alert('file info failed to load');
    });

    if (!binary.get('liveMode')) {
        sidebar.hideRaw();
    }
}

function InitializeComments() {

    console.debug('intializing comments...');

    $(document).on("keypress", ".comment", function(e) {

        console.debug("keypress " + e.which);

        if (e.which == 13)
        {
            // TODO: Save the comment
            $(this).blur()
        }

        if (e.which == 10)
        {
            // TODO: Handle <CTRL-Enter> and allow multi-line comments
        }

        return e.which != 13;
    });

    $(document).on("blur", ".comment", function(e) {

        var comment = $(this).html();
        var offset = $(this).parent().parent().attr("addr");

        // firefox needs at least a space to keep it editable
        if (comment == "" || comment == "<br>" ) {
            comment = "&nbsp;";
        } else {
            console.debug("adding comment at offset %s: \"%s\"", offset, comment);
            $.post("/odaweb/comment", { comment: comment, offset: offset } );

            // add "; "
            comment = "; " + comment;
        }

        $(this).html(comment);
    });

    $(document).on("focus", ".comment", function(e) {

        // on focus, delete the space that firefox requires for contenteditable spans
        if ($(this).html() == "&nbsp;") {
            $(this).html("");
        } else {
            // remove the "; "
            $(this).html($(this).html().substr(2));
        }
    });

    /*
    $(document).on("tooltip", ".comment", function(e) {
        placement: 'bottom',
        delay: { show: 100, hide: 100 },
        title: 'Add Comment',
        trigger: 'hover',
        content: 'Click to add a comment',
    });
    */
}

function InitializeModalShare() {

    // select the link in the text box when the modal is shown
    $('#modal-share').on('shown', function() {
        $("#share-url").select();
    });
}

$(document).ready(function(){

    sidebar.initialize();

    FileUploadTab();

    ResizeHandler();
    
    InitializeSplitter();

    InitializeComments();

    InitializeModalShare();

    LiveHex();
});