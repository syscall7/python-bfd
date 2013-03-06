

window.LiveHex = function() {
    var lastText = null;

    $('#hex').bind("keyup", function(e) {
        var newText = $('#hex').val();
        if (newText != lastText) {
            lastText = newText
            $.post('/odaweb/_set', {
                hex_val : newText
            }).done(function() {
                Load();
            });
        }
    });

};