window.LiveHex = function(binary) {
    var lastText = null;
    var idleTimer = undefined;

    var Reload = function() {

        idleTimer = undefined;

        var opts = $.map(
            $('.platform-option-select'), function(v) {return $(v).val();}
        );

        opts = $.grep(opts, function(e) { return e != "DEFAULT"});

        form_data = {
            options: opts,
            arch : $('#select-live-architecture').val(),
            base_address : $('#set-live-base-address').val(),
            hex_val : $('#hex').val(),
            endian : $('#hex-display .endian-select').val(),
            disassemble: true
        };

        $.post('/odaweb/_set', form_data)
            .done(function(response) {
            $('#hex-alert').hide();
            $('#live-mode-platform-options-form').html(response.form_html);
            Load(binary, true);
        }).fail(function(response){
            $('#hex-alert').show();
        });

    };

    $('#hex').bind("keyup", function(e) {
        var newText = $('#hex').val();
        if (newText != lastText) {
            lastText = newText;
            if (idleTimer != undefined)
                clearTimeout(idleTimer);
            idleTimer = setTimeout(Reload, 1000);
        }
    });

    /*$('#hex-display').on('change', '.platform-option-select', function(){
        Reload();
    })*/;

    /* catch ENTER key and reload with new base address */
    $('#set-live-base-address').live("keypress", function(e) {
        console.debug(e.keyCode);
        if (e.keyCode == 13) {
            event.preventDefault();
            $('#set-live-base-address').blur();
        }
    });

    /*$('#select-live-architecture').live("change", (function(){
        var arch = $('#select-live-architecture').val();
        // update arch in bottom right hand corner
        $('.platform-option').text(arch);
        Reload();

    })*/;

    $('#set-live-base-address').live("change", (function(){
        Reload();
    }));


};