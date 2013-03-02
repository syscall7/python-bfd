function FileUploadTab() {
    $('#fileselectbutton').click(function(e){
        $('#file').trigger('click');
    });

    $('#file').change(function(e){
        var val = $(this).val();

        var file = val.split(/[\\/]/);

        $('#filename').val(file[file.length-1]);
    });
}

function ResizeSidebarScroll(elem) {
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
}


function ResizeHandler() {
    $(window).resize(function() {
        // TODO: Hardcoded Height includes footer and banner
        /*$('#view-container').height($(window).height()-74);*/
        $('#vertSplitter').height($(window).height()-47);
        
        // TODO: Hardcoded Height includes footer, banner, and tabs
        $('#myTabContent').height($(window).height()-132);
             
        $('.sidebar-scroll-container').each( function (i,elem) {
            $(elem).height( ResizeSidebarScroll($(elem)) );} );
        
    });
    //$('#view-container').height($(window).height()-74);
    $('#vertSplitter').height($(window).height()-47);
    $('#myTabContent').height($(window).height()-132);
    $('.sidebar-scroll-container').each( function (i,elem) {
        $(elem).height( ResizeSidebarScroll($(elem)) );} );

    
}

function InitializeTabs() {

    $('.nav-btn').tooltip();
    $('.nav-btn').click(function(){
        $('sidebar .active').removeClass('active');
        $('.item').hide();
        $('#'+$(this).data('panel')).show();
    });

    $('#myTab a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    $('.item').hide();
    $('.active').show();
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
        if ( !updateDisassembly(addr) )
        {
            // Isn't loaded. Try to load it
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

function SidebarCloseHide() {
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

function Load(id) {

    var DisChunkInfo = Backbone.Model.extend({});
    var DisChunkList = Backbone.Collection.extend({
        model: DisChunkInfo
    });

    window.disChunks = new DisChunkList([]);


    $.post('_refresh', {id: id}).done(function(data){

        // Update the chunk list
        if ( data.chunks.length > 0 )
        {
            // Remove lower address chunks from the display
            $('#listing').find("tbody").remove();
    
            // Append the new listing
            $('#listing').find("colgroup").after(data.disassembly);

            // Remove lower address chunks from the display
            $('#hex-dump-table').find("tbody").remove();

            // Append the new listing
            $('#hex-dump-table').append(data.hex_dump);

            // Clear the collection
            window.disChunks.reset();
               
            // Append the new chunks to the end of the list
            for (var i = 0; i < data.chunks.length; i++) 
            {
                var chunk = new DisChunkInfo({ 
                    sec_name : data.chunks[i].sec_name,
                    startOffset : data.chunks[i].startOffset,
                    endOffset : data.chunks[i].endOffset,
                    lines : data.chunks[i].lines,
                    //hex_dump : data.chunks[i].lines,
                    isBoundary : data.chunks[i].isBoundary
                });
                window.disChunks.push(chunk);    
            }
        }
     
    }).fail(function(){
        alert('fail');
    });

    $.post('_symbols', {id: id}).done(function(data){
        $('#symbol-content').append(data.symbols_html);
        scrolify($('#symbol-table')); // 160 is height
        ResizeHandler();
    }).fail(function(){
        alert('symbols fail to load');
    });

    $.post('_sections', {id: id}).done(function(data){

        $('#tab-sections').append(data.sections_tab);

        SetupSectionFlagPopovers(data.section_flags);

    }).fail(function(){
        alert('sections failed to load');
    });
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

$(document).ready(function(){

    InitializeTabs();

    FileUploadTab();

    ResizeHandler();
    
    InitializeSplitter();

    InitializeComments();
});