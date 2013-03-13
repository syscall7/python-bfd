

window.LiveHex = function(binary) {
    var lastText = null;
    var refreshing = false;

    $('#hex').bind("keyup", function(e) {
        var newText = $('#hex').val();
        if (newText != lastText & !refreshing) {
            lastText = newText;
            refreshing = true;

            $.post('/odaweb/_set', {
                hex_val : newText
            }).done(function() {
                $('#hex-alert').hide();
                Load(binary);
                refreshing = false;
            }).fail(function(){
                $('#hex-alert').show();
                refreshing = false;
            });
        }
    });

};