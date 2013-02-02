
    function resizeHandler() {
    	  var myWidth = 0, myHeight = 0;
          var availableHeight = 0;  
    	  if( typeof( window.innerWidth ) == 'number' ) {
    	    //Non-IE 
    	    myWidth = window.innerWidth;
    	    myHeight = window.innerHeight;
    	  } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
    	    //IE 6+ in 'standards compliant mode' 
    	    myWidth = document.documentElement.clientWidth;
    	    myHeight = document.documentElement.clientHeight;
    	  } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
    	    //IE 4 compatible 
    	    myWidth = document.body.clientWidth;
    	    myHeight = document.body.clientHeight;
    	  }
    	  
    	  // Compute the size of the Tab object dynamically
    	  padding = 20
    	  offsetTop = $('#myTabContent').offset().top
    	  footerSize = $('footer').height()
    	  $('#myTabContent').height(myHeight - offsetTop - footerSize - padding)
    };
    
	$(document).ready(function() {
		resizeHandler();   
	});
	
    // Use a timer for dynamic sizing for performance reasons 
    var resizeTimer;
    $(window).resize(function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(resizeHandler, 100);
    });