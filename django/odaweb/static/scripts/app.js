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
        $('#view-container').height($(window).height()-74);
    });
    $('#view-container').height($(window).height()-74);
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


$(document).ready(function(){

    InitializeTabs();

    FileUploadTab();

    ResizeHandler();
});