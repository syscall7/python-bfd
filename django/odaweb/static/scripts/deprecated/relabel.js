$(document).ready(function() {

    $(".oda_label").keypress(function(e){

        if (e.which == 13)
        {
            // TODO: Save the new label name
            $(this).blur()
        }

        return e.which != 13;
    });

    $('.oda_label').blur(function() {

        // firefox needs at least a space to keep it editable
        if ($(this).html() == "" || $(this).html() == "<br>" ) {
            $(this).html("&nbsp;");
            // TODO: Don't allow empty names
        } else {
            // add any additional formatting or validation
        }

        // TODO: Save the new label name
    });

    $('.oda_label').focus(function() {
        // on focus, delete the space that firefox requires for contenteditable spans
        if ($(this).html() == "&nbsp;") {
            $(this).html("");
        } else {
            // remove any additional formatting
        }
    });

    $('.oda_label').tooltip({
        placement: 'bottom',
        delay: { show: 100, hide: 100 },
        title: 'Add Comment',
        trigger: 'hover',
        content: 'Click to rename this label',
        });
});
