var check=false;
var isRelative=true;

var router;

$(document).ready(function() {
	var WorkspaceRouter = Backbone.Router.extend({
		routes: {
			"view/:tab/offset/:offset" : "tab", //#calls function "tab" defined below
			"view/:tab" : "generic_tab" 
		},
        generic_tab : function(tab) {
            var tabselector = '#' + tab; 
            $(tabselector).tab('show');
		},
		tab : function(tab,offset) {
			if ( tab == 'assembly-tab-item')
			{
				var assembly_position = window.assembly_position; 

				// Select the assembly tab
				var tabselector = '#' + tab;
			    $(tabselector).tab('show');
				
				// Check if the target offset is currently loaded in the browser
				var intOffset = parseInt(offset,16);
                if ( !updateDisassembly(intOffset) )
                {
                    // Need to handle the scroll if the window isn't changing
                    scrollToAddr(intOffset);                    
                }                							
			} 
		}
		
	});

    window.ignoreScrollEvents = false;
    window.scrollTimer=null;
	
	router = new WorkspaceRouter();
	Backbone.history.start();
	

	$('#myTabContent').bind('scrollstop', assemblyScrollStopHandler);
    $('#myTabContent').bind('scroll', function(event) {
            if ( window.scrollTimer == null )
            {
                //console.debug("Set timer for 100ms latency\n");
                window.scrollTimer = setTimeout(assemblyScrollHandler, 100);                
            }
        });
        
    // Use a timer for dynamic sizing for performance reasons 

	$('a[data-toggle="tab"]').on('shown', function(e) {
		
		// Don't navigate to tabs that are already showing
        var t = $(e.target).attr('href').replace('#','')
		if( window.location.hash.indexOf( t + '-tab-item' ) == -1 )
		{
            router.navigate("view/" + t + '-tab-item');
	    } 
	})

});


function scrollToAddr(offset)
{
    console.debug("scrollToAddr, offset %s", offset.toString(16));

    // go back up to 16 bytes
    var tries = 16;

    while (offset > 0 && tries > 0) {
        // Convert to a hex string with leading zeroes
        var hexStr = ("000000000000000" + offset.toString(16)).substr(-8);

        // Scroll to the proper offset in the disassembly
        var offsetselector = 'tr[addr=' + hexStr + ']';
        var offset_element = $(offsetselector);

        if ( offset_element.length > 0 )
        {
            var dbar_height = $('#download-bar').outerHeight(true);
            var disoffset_top = offset_element[0].offsetTop;

            console.debug("scrollToAddr, scrollTop %d", disoffset_top + dbar_height + 1);

            // Row element offset doesn't include size of the download bar
            $('#myTabContent').scrollTop(disoffset_top + dbar_height + 1);
            return true;
        }

        tries--;
        offset--;
    }

    // Offset doesn't exist
    return false;
}

function updateDisassembly(offset)
{
    console.debug("updateDisassembly, start");

    var chunks = window.disChunks;

    // Map the offset to a chunk
    var index = getChunkIndex(offset);
    console.debug("updateDisassembly, got chunk index %d", index);

    // Determine how many new chunks to request
    var mid_index = Math.floor((chunks.length/2));
    if ( index == -1 )
    {
        // Need to load all new disassembly
        console.debug("updateDisassembly, refresh entire page");
        window.refresh(offset);
        return true;
    }
    else if ( index > mid_index )
    {
        // Partial load
        console.debug("updateDisassembly, partial load forward");
        var requested_chunks = index-mid_index;
        return requestMoreDisassembly(1,requested_chunks,offset);
    }
    else if ( index < mid_index )
    {
        // Partial load
        console.debug("updateDisassembly, partial load reverse");
        var requested_chunks = mid_index - index;
        return requestMoreDisassembly(0,requested_chunks,offset);        
    }
    
    return false;                
}


function getChunkIndex(offset)
{
    // Find the chunk that contains the address
    var chunks = window.disChunks;
    for (var i = 0; i < chunks.length; i++) 
    {
        var start = chunks.models[i].get('startOffset');
        var end = chunks.models[i].get('endOffset');
        if ( offset >= start && offset < end )
        {
            return i;
        }
    }
    
    // Chunk not found or address not on the page
    return -1;
    
}

function requestMoreDisassembly(dir,chunk_count,offset)
{
    var lines = 0;
    if ( chunk_count < window.disChunks.length )
    {
        // Keeping some of the existing window
        var chunks = window.disChunks;
        var index = 0;
        
        if ( dir == 1 )
        {
            // Append new chunks
            index = chunks.length-1;            
        }
        else
        {
            // Prepend new chunks
            index = 0;
        }

        // Check if we can request more chunks
        if ( chunks.models[index].get('isBoundary') == false )
        {
            // Append new chunks to the bottom
            window.ignoreScrollEvents = true;
            getMore(chunks.models[index].get('sec_name'),
                    chunks.models[index].get('startOffset'),
                    chunks.models[index].get('endOffset'),
                    chunk_count,
                    dir,
                    offset);
            
            return true;            
        }
    }
    
    return false;
    
}


function myElementFromPoint(x,y)
{
    if(!check)
    {
      var sl;
      if((sl = $(document).scrollTop()) >0)
      {
       isRelative = (document.elementFromPoint(0, sl + $(window).height() -1) == null);
      }
      else if((sl = $(document).scrollLeft()) >0)
      {
       isRelative = (document.elementFromPoint(sl + $(window).width() -1, 0) == null);
      }
      check = (sl>0);
    }

    if(!isRelative)
    {
      x += $(document).scrollLeft();
      y += $(document).scrollTop();
    }

    return document.elementFromPoint(x,y);
}

function getTopVisibleAssemblyRow()
{
    // Find the position of the top most disassembly line
    var main_contain_left = $("#main-container")[0].offsetLeft;
    var main_contain_top = $("#main-container")[0].offsetTop;
    var dbar_left = $('#download-bar')[0].offsetLeft;
    var dbar_top = $('#download-bar')[0].offsetTop; 
    var dbar_border_width = 1;  // Could get from .css

    console.debug("getTopVisibleAssemblyRow main_left %d, main_top %d, dbar_left %d, dbar_top %d",
        main_contain_left, main_contain_top, dbar_left, dbar_top);
    
    // Calculate the first pixel of the top-most visible disassembly line
    var target_top = main_contain_top + dbar_top + 1;
    
    // Calculate the left most pixel of the top-most visible disassembly line
    var target_left = main_contain_left + dbar_left + + dbar_border_width + 1;
    
    // Get the Line of disassembly to determine the corresponding address
    var elem = myElementFromPoint(target_left, target_top);

    // Handle labels and other internal tags
    if ( elem.id == 'download-bar')
    {
        // The dbar is at the top of the listing so just skip to the first row
        elem = $('#listing').find('tr').first()[0];
    }
    else if ( elem.tagName.toLowerCase() != 'tr' )
    { 
        // Most likely in an internal tag (tr.branchlines, etc)
        elem = $(elem).closest('tr')[0];
    } 

    return elem;    
}



function assemblyScrollHandler() 
{
    console.debug("assemblyScrollHandler, start");
    //var ignore = ignoreScrollEvents;
    //ignoreScrollEvents = false;    
    if (window.ignoreScrollEvents) 
    {
        window.scrollTimer=null;
        console.debug("assemblyScrollHandler, ignoring scroll events");
        return;
    }

    console.debug("Scroll Handler fired\n");

    var elem = getTopVisibleAssemblyRow();
    if (elem) { 
        var intOffset = parseInt(elem.getAttribute("addr"),16);

        console.debug("assemblyScrollHandler, updating slider to ", elem.getAttribute("addr"));
        updateSlider(intOffset);

        // Load Code if necessary
        if ( !updateDisassembly(intOffset) )
        {
            window.scrollTimer=null;
        }
    } 
    else
    {
        window.scrollTimer=null;        
    }
}

function assemblyScrollStopHandler() 
{
    console.debug("assemblyScrollStopHandler, start");
	var elem = getTopVisibleAssemblyRow();
	
	if (elem) { 
        var url_hash_params = {};
        var offsetStr = elem.getAttribute("addr");
        url_hash_params.tab = "assembly-tab-item";
		url_hash_params.offset = offsetStr;

        var intOffset = parseInt(offsetStr,16);
        console.debug("assemblyScrollStopHandler, updating slider to ", offsetStr);
        updateSlider(intOffset);

        // Update the URL
    	router.navigate("view/"+url_hash_params.tab + "/offset/" + url_hash_params.offset);
    	
    	// Load code if necessary
    	//var intOffset = parseInt(url_hash_params.offset,16);
    	//updateDisassembly(intOffset);
    }
}

// update slider position via non-slider events (i.e., via scrollBar)
function updateSlider(addr) {
    //updateAddrDisplay(addr);
    $("#slider").slider("value", addr);
}


