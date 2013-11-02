var Binary = Backbone.Model.extend({

});

var oda = oda || {};

oda.url = function(url) {
    return '/odaweb/' + url;
};

oda.alert = function(message) {
    $('.top-right').notify({
        message: { text: message },
        fadeOut: { enabled : false }
    }).show();
};

var commentEditing = false;
var dialogOpen = false;

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
            $(this).tab('show');
            var jtab = $(this);
            if ( isScrollableTab(window.activeTab) )
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
        var new_height;
        if ( $(elem).find('table').length )
        {
            // Table header height
            new_offset += 36;
            new_offset += $("#sidebar").offset().top + accum_margins;
            new_height = $(window).height()-new_offset;            
        }
        else if ( $(elem)[0].type == 'textarea' )
        {
            // Live View 
            var hexOffset = $("#hex-sidebar-scroll").offset().top;
            new_height = $(window).height() - hexOffset - accum_margins;
        }
        else
        {
            // Margins and Padding
            new_offset += 15;
            new_offset += $("#sidebar").offset().top + accum_margins;
            new_height = $(window).height()-new_offset;
        }
        return new_height;  //237;
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

    var LoadPlatformOptions = function() {
        var values = $.map(
            $('.platform-option-select'), function(v) {return $(v).val();}
        );

        values = $.grep(values, function(e) { return e != "DEFAULT"});
    };

    $('.platform-option-select').on('change', LoadPlatformOptions);
    $('#form-platform-options').submit(function(e) {
        LoadPlatformOptions();
        e.preventDefault();
    });

    $('#select-open-architecture').change(function(){
        var arch = $('#select-open-architecture').val();

        LoadOptions(arch);

        //$('.platform-option').text(arch);

    });

    $('#upload-options-submit-btn').click(function(e) {
        var arch = $('#select-open-architecture').val();
        var base_address = $('#set-open-base-address').val();
        var values = $.map(
            $('.platform-option-select'), function(v) {return $(v).val();}
        );

        values = $.grep(values, function(e) { return e != "DEFAULT"});

        /* TODO: catch form errors and redisplay form here */
        $.post('/odaweb/_set', {arch: arch, base_address: base_address, options: values})
            .done(function() {
                var foobar = $('#modal-open-platform-options-short-name').val();
                window.location = "/odaweb/" + $('#modal-open-platform-options-short-name').val();
            }).fail(function(){
            });

        e.preventDefault();
    });
}

function FileUploadForm() {

    FileUploadOptionsForm();

    $('#open-btn').on('click', function(e) {
        dialogOpen = true;
        $('#modal-upload-form').modal();
    });

    $('#modal-upload-form').on('click', '#fileselectbutton', function(e){
        $('#file').trigger('click');
    });
    
    $('#modal-upload-form').on('hidden', function () {
        dialogOpen = false;
    })

    $('#modal-upload-form').on('change', '#file', '', function(e){
        var val = $(this).val();

        var file = val.split(/[\\/]/);

        $('#filename').val(file[file.length-1]);
    });

    // called when upload form button is clicked
    $('#modal-upload-form').on('click', '#upload-submit-btn', '', function(e){
        dialogOpen = false;

        // use handy plugin for ajax submissions of file uploads
        $('#upload-form').ajaxSubmit({
            dataType: 'json',
            success: function(data) {

                // if there were no errors in the form
                if (data.html == '') {

                    // default to i386 for unknown arch
                    default_arch = 'i386';

                    // if we do know the arch...
                    if (data.arch != 'UNKNOWN!') {
                        default_arch = data.arch;
                    }

                    $('#modal-upload-form').modal('hide');

                    form_data = {
                        arch : default_arch,
                        base_address : ""
                    };

                    $.post('/odaweb/_set', form_data)
                        .done(function(response) {

                            $('#select-open-architecture').val(default_arch);
                            $('#select-open-architecture').change();
                            $('#modal-platform-msg').html(data.msg);
                            $('#modal-platform-options-form').html(response.form_html);
                            $('#modal-open-platform-options-short-name').val(data.id);
                            $('#modal-platform-options').modal();

                            // if we cannot detect the file format
                            if (data.arch == 'UNKNOWN!') {

                                // let the user select the arch AND options
                                $('#select-open-architecture').prop('disabled', false);
                                $('#set-open-base-address').prop('disabled', false);
                            }
                            // else, we know the format (and should therefore already know the arch)
                            else {

                                // let the user select only select the options
                                $('#select-open-architecture').prop('disabled', true);
                                $('#set-open-base-address').prop('disabled', true);
                            }

                        }).fail(function(response){
                            $('#modal-upload-form').html(data.html);
                        });

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
        $('#myTabContent').height($(window).height()-157);
             
        $('.sidebar-scroll-container').each( function (i,elem) {
            $(elem).height( sidebar.resize($(elem)) );} );
        
    });
    //$('#view-container').height($(window).height()-74);
    $('#vertSplitter').height($(window).height()-47);
    $('#myTabContent').height($(window).height()-157);
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
                oda.alert('Address must be hexadecimal in the form of "AABB..." or "0xAABB..."');
                continue;
            }
            // must be within range
            else if ((addr < min) || (addr > max)) {
                addr = NaN;
                oda.alert('Address must be in the range 0x' + min.toString(16) + ' to  0x' + max.toString(16));
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
    if ( !updateDisplayedFileContent(addr,false) )
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
            updateDisplayedFileContent(addr,false);
            scrollToAddr(addr);
        }
    }

    // setup slider
    $( "#slider" ).slider({
        change: function( event, ui ) { updateAddrDisplay(ui.value); },
        slide: function( event, ui ) { updateAddrDisplay(ui.value); },
        stop: function( event, ui )  { sliderHandler(ui.value); },
        animate: true,
        min: min,
        max: max,
    });

    // set initial position
    window.initialOffset = min;
    window.activeTab = "tab-assembly";
    updateAddrDisplay($("#slider").slider("value"));

    $(document).on("click", "#listing tr", function(){
        selectedRow = $(this);
        $('tr.selected').removeClass('selected');
        $(this).addClass('selected');
    });
    $(document).on("hover", "#listing tr", function(){
        updateAddrDisplay($(this).attr('addr'));
    });

    $("html").keypress(function(event) {
        if (String.fromCharCode(event.which) == 'g' && !commentEditing && !dialogOpen) {
            GoToAddressPrompt();
        }
        else if (String.fromCharCode(event.which) == ';') {

            if (selectedRow != null) {
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
    window.hexChunks = new window.DisChunkList([]);

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
    
    refreshDisassembly(addr,  show_loading);
    refreshHex(addr,false);
    
    $.post(oda.url('_symbols'), {id: binary.id}).done(function(data){
        $('#symbol-content').append(data.symbols_html);
        scrolify($('#symbol-table')); // 160 is height
        ResizeHandler();
    }).fail(function(){
        oda.alert('symbols fail to load');
    });

    /* $.post(oda.url('_strings'), {id: binary.id}).done(function(data){
        $('#strings-content').append(data.strings);
        scrolify($('#strings-table')); // 160 is height
        ResizeHandler();
    }).fail(function(){
            oda.alert('strings fail to load');
    }); */

    $.post(oda.url('_sections'), {id: binary.id}).done(function(data){

        //$('#tab-sections').html(data.sections_tab);

        SetupSectionFlagPopovers(data.section_flags);

    }).fail(function(){
        oda.alert('sections failed to load');
    });

    $.post(oda.url('_fileinfo'), {id: binary.id}).done(function(data){

        $('#tab-fileinfo').html(data.fileinfo_tab);
        $('#known-malware').popover();
        $('#known-benign').popover();

    }).fail(function(){
        oda.alert('file info failed to load');
    });

    /* This was used to display the user's existing file
    $.post('_owned_files', {id: binary.id}).done(function(data){
        $('#open-existing-list').html(data.file_list_html)
    }).fail(function(){
        oda.alert('failed to load owned files');
    });
    */
}

function InitializeComments() {

    $(document).on("keypress", ".comment", function(e) {

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
        commentEditing = false;

        var comment = $(this).html();
        var offset = $(this).parent().parent().attr("addr");

        // firefox needs at least a space to keep it editable
        if (comment == "" || comment == "<br>" ) {
            comment = "&nbsp;";
        } else {
            $.post("/odaweb/comment", { comment: comment, offset: offset } );

            // add "; "
            comment = "; " + comment;
        }

        $(this).html(comment);
    });

    $(document).on("focus", ".comment", function(e) {
        commentEditing = true;

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

function InitializeRelabeling() {

    $(document).on("keypress", ".listing-label", function(e) {

        if ((e.which == 13) || (e.which == 10))
        {
            $(this).blur()
        }

        return e.which != 13;
    });

    $(document).on("blur", ".listing-label", function(e) {
        commentEditing = false;

        var label = $(this).html();
        var offset = $(this).parent().parent().attr("addr");

        // firefox needs at least a space to keep it editable
        if (label == "") {
        } else {
            $.post("/odaweb/relabel", { label: label, offset: offset } );
        }

        $(this).html(label);
    });

    $(document).on("focus", ".listing-label", function(e) {
        commentEditing = true;
        // TODO: Save off the original name in order to restore on ESC
    });
}

function InitializeModalShare() {

    // select the link in the text box when the modal is shown
    $('#modal-share').on('shown', function() {
        $("#share-url").select();
    });
}

function OdaApplication(options) {

    if (options.saved) {

        // show the popover, but don't close it when clicked
        $('#menu-item-share').popover('show').click(function(evt) {
            evt.stopPropagation();
            $(this).popover('show');
        });

        // close the popover when clicked anywhere outside the popover
        setTimeout(function(){
            $('html').click(function() {
                $('#menu-item-share').popover('hide');
            });
        }, 500);
    }

    $('#whats-oda-btn').on('click', function(e) {
        $('#modal-whats-oda').modal();
    });

    $('#about-oda-btn').on('click', function(e) {
        $('#modal-about').modal();
    });

    sidebar.initialize(options.binary.get('liveMode'));

    FileUploadForm();

    ResizeHandler();

    InitializeSplitter();

    InitializeComments();

    InitializeRelabeling();

    InitializeModalShare();

    InitializeMenus();

    LiveHex(options.binary);

    Load(options.binary);
}