$(document).ready(function() {   
		
	var running = false;

    var get_upload_data = function() {
        // Convert all existing options to a single string
        //    separated by -- for each value,index and ---
        //    for each set
        var blkstr = [];
        $.each(window.runHexOptions, function(idx2,val2) {
            var str = idx2 + "--" + val2;
            blkstr.push(str);
        });
        str = blkstr.join("---");
        var upload_data = {
            hex_val : $('#hex').val(),
            options : str,
            offset : 'here',
            platformId : $('#platformSelect').val()
        };
        return upload_data;
    };


    var WorkspaceRouter = Backbone.Router.extend({
        routes: {
            "save" : "save"
        },
        save : function() {
            $.post('/odaweb/save', get_upload_data(), function() {

            });
            window.location = "/odaweb/run_hex/dude";
        }
    });

    var router = new WorkspaceRouter();
    Backbone.history.start();
		
	var load = function() {
		if (running)
			return; 
		running = true; 
		rotate_gear();
		

		 $('#disassembly').load('disassemble/uploadHex',get_upload_data(),
		 function(response, status, xhr) {
			if (status == "error") {

		    }

			stop_gear();
			running = false;
		});
	}

    if ( !window.runHexOptions )
    {
        $('#platformSelect').val('i386');
        window.runHexOptions = {};
        window.load = load;
    } 

    var showOptions = function() {
        var blkstr = [];
        $.each(window.runHexOptions, function(idx2,val2) {                    
            var str = idx2 + "--" + val2;
            blkstr.push(str);
        });
        str = blkstr.join("---");

        $('#myModal').load('disassemble/showOptions',
        { 
            platformId : $('#platformSelect').val(),
            options : str
        }, function(response, status, xhr) {
            if (status == "error") {

            }
            $("#myModal").modal();   
        });
    }
	
	$('#platformSelect').change(function(){
	    window.runHexOptions = {};		
		load(); 
	});
	
	//$('#endianSelect').change(function(){		
	//	load(); 
	//});
	    
    $('#optionsBtn').click(function () {
        showOptions();
    })
    

	$('#hex').keyup(function() { 
		load();
	}); 
	load(); 
	
	var examples = {
		strCpyArm : {
			arch: 'arm', 
			hex : '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1 '
		}, 
		strCpyX86 : {
			arch: 'i386',
			hex: '55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3 ' 
		}
	}
	
	var do_example = function(ex) {
         window.runHexOptions = {};      
		 $('#hex').val(ex.hex);
		 $('#platformSelect').val(ex.arch);
		 load();
	}
	
	$('#selectExamples').change(function(){		
		if ($(this).val() == "strcpy (arm)") 
			do_example(examples.strCpyArm); 
		else if ($(this).val() == "strcpy (x86)") 
			do_example(examples.strCpyX86); 
		
	}); 
/*	
	$("#example-strcpy-arm").click(function(){
		do_example(examples.strCpyArm); 
	}); 
	$("#example-strcpy-x86").click(function(){
		do_example(examples.strCpyX86); 
	}); */
	
}); 