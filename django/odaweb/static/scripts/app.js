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
    })

    $('.item').hide();
    $('.active').show();
}

function InitializeSplitter() {
    $("#main-display").splitter({type: 'v'});    
}

function InitializeSlider() {
    // setup slider
    $( "#slider" ).slider({
        animate: true,
        min: 0x00000000,
        max: 0xFFFFFFFF,
    });

    // remove border
    $(".ui-slider-horizontal").css('border', 0);
    $(".ui-slider-handle").removeClass('ui-corner-all');
    
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

        console.debug("blur");

        var comment = $(this).html();
        //window.comment("12345678", comment);

        // firefox needs at least a space to keep it editable
        if (comment == "" || comment == "<br>" ) {
            comment = "&nbsp;";
        } else {
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

    InitializeSlider();

    InitializeComments();

});