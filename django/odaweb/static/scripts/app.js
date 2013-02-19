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

function ResizeHandler() {
    $(window).resize(function() {
        // TODO: Hardcoded Height includes footer and banner
        $('#view-container').height($(window).height()-74);
        $('#vertSplitter').height($(window).height()-47);
        
        // TODO: Hardcoded Height includes footer, banner, and tabs
        $('#myTabContent').height($(window).height()-152);
             
        $('#sidebar-container').height($(window).height()-47);
        $('sidebar-content').height($(window).height()-197);
    });
    $('#view-container').height($(window).height()-74);
    $('#vertSplitter').height($(window).height()-47);
    $('#myTabContent').height($(window).height()-152);
    $('#sidebar-container').height($(window).height()-47);
    $('sidebar-content').height($(window).height()-197);

    
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

        /* TODO: Uncomment this after porting over history.js
        // Try to scroll to the address
        if ( !updateDisassembly(addr) )
        {
            // Isn't loaded. Try to load it
            scrollToAddr(addr);
        }
        */
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

function Load(id) {

    $.post('_refresh', {id: id}).done(function(data){

        $('#listing').find("tbody").remove();

        // Append the new listing
        $('#listing').find("colgroup").after(data.disassembly);

    }).fail(function(){
        alert('fail');
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
            $.post("/odaweb/comment/", { comment: comment, offset: offset } );

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