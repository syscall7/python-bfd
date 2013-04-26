var Binary = Backbone.Model.extend({

});

var Sidebar = Backbone.Model.extend({
    initialize : function(liveMode) {

        $('.nav-btn').tooltip();
        $('.nav-btn').click(this, function(event){
            $('#sidebar .active').removeClass('active');
            $('.item').hide();
            $('#'+$(this).data('panel')).show();
            event.data.set('active_tab', $('#'+$(this).data('panel')).attr('id'));
        });

        $('#myTab a').click(function (e) {
            e.preventDefault();
            window.activeTab = e.target.hash.split('#')[1];
            console.debug("WindowActivetab %s %s",window.activeTab,window.lastAddr.toString(16));
            $(this).tab('show');
            var jtab = $(this);
            if ( window.activeTab == "tab-assembly" )
            {
                router.navigate("view/"+ window.activeTab + "/offset/" + intToHexStr(window.lastAddr), {trigger: true});
            } 
            else
            {
                router.navigate("view/"+ window.activeTab, {trigger: true});
            }
        });

        $('.item').hide();
        $('.active').show();

        if (liveMode) {
            $('#sidebar-tools').hide();
        } else {
            $('#hex-display-btn').hide();
            $('#symbols-btn').click();
        }
    },

    resize : function(elem) {
        var new_offset = $("#sidebarContent").offset().top;
        var accum_margins = 15; //Not captured by jquery
        if ( $(elem).find('table').length )
        {
            // Table header height
            new_offset += 36;
        }
        else if ( $(elem)[0].type == 'textarea' )
        {
            // Hex Dump has a help banner.
            //  TODO: Calculate this programatically
            new_offset += 120;
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

function FileUploadOptionsForm() {

    var LoadOptions = function(arch) {
        $.post('/odaweb/_options', {platformId : arch})
            .done(function(data){
                $('#open-platform-options').html(data);
            });
    };

    $('.platform-option-select').on('change', function(){
        var values = $.map(
            $('.platform-option-select'), function(v) {return $(v).val();}
        );

        values = $.grep(values, function(e) { return e != "DEFAULT"});
    });

    $('#select-open-architecture').change(function(){
        var arch = $('#select-open-architecture').val();

        LoadOptions(arch);

        //$('.platform-option').text(arch);

    });

    $('#upload-options-submit-btn').click(function(e) {
        var arch = $('#select-open-architecture').val();
        var values = $.map(
            $('.platform-option-select'), function(v) {return $(v).val();}
        );

        values = $.grep(values, function(e) { return e != "DEFAULT"});

        $.post('/odaweb/_set', {arch: arch, options: values})
            .done(function() {
                window.location = "/odaweb/" + $('#modal-platform-options-short-name').val();
            }).fail(function(){
            });

        e.preventDefault();
    });
}

function FileUploadForm() {

    FileUploadOptionsForm();

    $('#open-btn').on('click', function(e) {
        $('#modal-upload-form').modal();
    });

    $('#modal-upload-form').on('click', '#fileselectbutton', function(e){
        $('#file').trigger('click');
    });

    $('#modal-upload-form').on('change', '#file', '', function(e){
        var val = $(this).val();

        var file = val.split(/[\\/]/);

        $('#filename').val(file[file.length-1]);
    });

    // called when upload form button is clicked
    $('#modal-upload-form').on('click', '#upload-submit-btn', '', function(e){

        // use handy plugin for ajax submissions of file uploads
        $('#upload-form').ajaxSubmit({
            dataType: 'json',
            success: function(data) {

                // if there were no errors in the form
                if (data.html == '') {

                    $('#modal-upload-form').modal('hide');
                    $('#select-open-architecture').val(data.arch);
                    $('#select-open-architecture').change();
                    $('#modal-platform-options-short-name').val(data.id);
                    $('#modal-platform-options').modal();
                    $('#modal-platform-msg').html(data.msg);

                    // if we cannot detect the file format
                    if (data.target == 'binary') {
                        console.debug('File format not detected');
                        $('#select-open-architecture').prop('disabled', false);
                    }
                    // else, we know the format (and should therefore already know the arch)
                    else {
                        $('#select-open-architecture').prop('disabled', true);
                    }

                }
                // else there were errors in the form
                else {
                    $('#modal-upload-form').html(data.html);
                }


            }
        });
    });
}

function ResizeHandler() {
    $(window).resize(function() {
        // TODO: Hardcoded Height includes footer and banner
        /*$('#view-container').height($(window).height()-74);*/
        $('#vertSplitter').height($(window).height()-47);
        
        // TODO: Hardcoded Height incluees footer, banner, and tabs
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

function GoToAddressPrompt() {

    var addr;

    var min = $("#slider").slider("option", "min");
    var max = $("#slider").slider("option", "max");

    // continue prompting until they get it right or give up
    do {

        var strAddr = prompt("Go to address:");

        // if Cancel was not hit and the user actually entered something
        if (strAddr) {

            // prepend '0x'
            if (strAddr.substring(0,2) != '0x')
                strAddr = '0x' + strAddr;

            addr = Number(strAddr);
            // must be a number
            if (isNaN(addr)) {
                console.debug("Not a number!");
                alert('Address must be hexadecimal in the form of "AABB..." or "0xAABB..."');
                continue;
            }
            // must be within range
            else if ((addr < min) || (addr > max)) {
                addr = NaN;
                alert('Address must be in the range 0x' + min.toString(16) + ' to  0x' + max.toString(16));
                continue;
            }

        }
        // else, Cancel was clicked
        else {
            return;
        }
    } while (isNaN(addr));

    // update slider
    $("#slider").slider("value", addr );

    // Try to scroll to the address
    if ( !updateDisassembly(addr) )
    {
        // Isn't loaded. Try to load it
        scrollToAddr(addr);
    }
}

function InitializeMenus() {
    $('#menu-go-to-addr').click(function(e) {
        GoToAddressPrompt();
    });
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
        //console.debug("updateAddrDisplay to %s", addrStr);
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
    window.initialOffset = min;
    window.activeTab = "tab-assembly";
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
            GoToAddressPrompt();
        }
        else if (String.fromCharCode(event.which) == ';') {

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

function Load(binary, show_loading) {

    if (arguments.length == 1) {
        show_loading = true;
    }

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
    
    console.debug("Load, refreshDisassembly addr= 0x%s",addr.toString(16));    
    refreshDisassembly(addr,  show_loading);
    
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
            alert('strings fail to load');
    });

    $.post('_sections', {id: binary.id}).done(function(data){

        $('#tab-sections').html(data.sections_tab);

        SetupSectionFlagPopovers(data.section_flags);

    }).fail(function(){
        alert('sections failed to load');
    });

    $.post('_fileinfo', {id: binary.id}).done(function(data){

        $('#tab-fileinfo').html(data.fileinfo_tab);

    }).fail(function(){
        alert('file info failed to load');
    });

    $.post('_owned_files', {id: binary.id}).done(function(data){
        $('#open-existing-list').html(data.file_list_html)
    }).fail(function(){
        alert('failed to load owned files');
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
            $(this).html($(this).text().substr(2));
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

function OdaApplication(binary) {

    sidebar.initialize(binary.get('liveMode'));

    FileUploadForm();

    ResizeHandler();

    InitializeSplitter();

    InitializeComments();

    InitializeModalShare();

    InitializeMenus();

    LiveHex(binary);

    Load(binary);
}