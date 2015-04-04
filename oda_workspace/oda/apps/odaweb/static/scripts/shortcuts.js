odaApplication.run(function($rootScope, Docker, odbFile, editor){

    //http://dmauro.github.io/Keypress/
    var listener = new window.keypress.Listener($('#editor')[0]);


    listener.simple_combo("ctrl g", function() {
        console.log("You pressed ctrl g");
        //todo activate textbox
        $rootScope.$broadcast('command.goto');
    });

    listener.simple_combo(';', function(){
         $rootScope.$broadcast('command.comment');
    });

    listener.simple_combo('c', function(){
        var activeRowData = editor.getActiveRowData();

        $rootScope.$broadcast('command.dataToCode', activeRowData);
    });

    listener.simple_combo('d', function(){
        var activeRowData = editor.getActiveRowData();

        $rootScope.$broadcast('command.codeToData', activeRowData);
    });

    listener.simple_combo("ctrl u", function(){
        $rootScope.$broadcast('command.open');
    });

    listener.simple_combo("t", function(){
        $rootScope.$broadcast('command.makeStructType');
    });

    listener.simple_combo('v', function(){
        var session = editor.getSession();

        var cursor = session.getSelection().getCursor();
        var line = session.getDocument().getLineData(cursor.row);

        $rootScope.$broadcast('command.makeStructVariable', {
            line: line
        });
    });

    listener.simple_combo("ctrl f", function(){
        $rootScope.$apply(function(){Docker.select(Docker.docks[2]);});
    });
});