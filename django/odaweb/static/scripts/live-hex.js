

window.LiveHex = function(binary) {
    var lastText = null;
    var refreshing = false;

    var Reload = function(data) {

        refreshing = true;

        $.post('/odaweb/_set', data)
            .done(function() {
            $('#hex-alert').hide();
            Load(binary, false);
            refreshing = false;
        }).fail(function(){
            $('#hex-alert').show();
            refreshing = false;
        });

    };

    $('#hex').bind("keyup", function(e) {
        var newText = $('#hex').val();
        if (newText != lastText & !refreshing) {
            lastText = newText;

            Reload({
                hex_val : newText
            })
        }
    });

    $('#select-live-architecture').change(function(){
        var arch = $('#select-live-architecture').val()
        Reload({
            arch : arch
        });

        $('.platform-option').text(arch);
    });

};