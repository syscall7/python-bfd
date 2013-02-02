function rotate_gear() {
	$("#oda-gear").show();
}


function stop_gear() {
	$("#oda-gear").hide();
}

$(document).ready(function() {
	$("#selectFile").change(function() {
		if ($(this).val()) { 
		v = $(this).val().split(',');
		document.location.href="/odaweb/disassemble/"+v[0]+"?platformId="+v[1];
		}
	}); 
}); 