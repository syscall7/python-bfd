$(document).ready(function() {

    $(".comment").keypress(function(e){

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

    $('.comment').blur(function() {
        // TODO: Save the comment

        // firefox needs at least a space to keep it editable
        if ($(this).html() == "" || $(this).html() == "<br>" ) {
            $(this).html("&nbsp;");
        } else {
            // add "; "
            $(this).html("; " + $(this).html());
        }
    });

    $('.comment').focus(function() {
        // on focus, delete the space that firefox requires for contenteditable spans
        if ($(this).html() == "&nbsp;") {
            $(this).html("");
        } else {
            // remove the "; "
            $(this).html($(this).html().substr(2));
        }
    });

    $('.comment').tooltip({
        placement: 'bottom',
        delay: { show: 100, hide: 100 },
        title: 'Add Comment',
        trigger: 'hover',
        content: 'Click to add a comment',
        });
});
