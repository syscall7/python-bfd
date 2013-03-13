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
			    // Only process tabs for existing sessions
			    //   In other words, you can't navigate to an address
			    //   by typing in the URL if you haven't already started
			    //   a session
			    if (typeof window.disId === "undefined") 
			    {
			        // Save the initial offset for use by the Load function
			        window.initialOffset = parseInt(offset,16);
			        console.debug("Save Initial Offset %d %x %d %x",window.initialOffset,window.initialOffset,offset,offset)    
			    }
			    else
			    {
    				var assembly_position = window.assembly_position; 
    
    				// Select the assembly tab
    				var tabselector = '#' + tab;
    			    $(tabselector).tab('show');
    				
    				// Check if the target offset is currently loaded in the browser
    				var intOffset = parseInt(offset,16);
    				console.debug("tab, updateDisassembly offset %s", intOffset.toString(16));
                    if ( !updateDisassembly(intOffset) )
                    {
                        // Need to handle the scroll if the window isn't changing
                        scrollToAddr(intOffset);                    
                    }                				
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

            console.debug("scrollToAddr, scrollTop %x", disoffset_top + dbar_height + 1);

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

function loadPopovers()
{
    $('insn').popover({
        placement: 'left',
        trigger: 'hover',
        html : true,
        title : function() {
            var instruction = $(this).text();
            var re = /^\s*(\w+)\s*.*$/;
            match = re.exec(instruction);
            return match[1];
        },
        content : function(e) {
            var instruction = $(this).text();
            var re = /^\s*(\w+)\s*.*$/;
            var mnemonic = re.exec(instruction)[1];

            $.ajax({
                type: 'POST',
                url: '_instdoc',
                data: {mnemonic: mnemonic},
                // Must be a blocking request in order for popopver to work for the very first hover
                async: false,
                success: function(instdoc_data){
                    $('#popover-inst-doc').html(instdoc_data.instdoc);
                },
                error: function(){
                    $('#popover-inst-doc').html("Failed to fetch instruction documentation.");
                }
            });

            return $('#popover-inst-doc').html();
        }
    });    
}


// Load an entire new page of disassembly
function refreshDisassembly(offset)
{
	console.debug("refreshDisassembly, start");
    $.post('_refresh', {id: window.disId, addr:offset}).done(function(data){

        $('#loading-panel').hide();

        // Update the chunk list
        if ( data.chunks.length > 0 )
        {
            // Remove old chunks from the display
            console.debug("refreshDisassembly, remove old listing");
            $('#listing').find("tbody").remove();
    
            // Append the new listing
            console.debug("refreshDisassembly, append new listing");
            $('#listing').find("colgroup").after(data.disassembly);

            // Remove old chunks from the display
            console.debug("refreshDisassembly, remove old hex");
            $('#hex-dump-table').find("tbody").remove();

            // Append the new listing
            console.debug("refreshDisassembly, append new hex");
            $('#hex-dump-table').append(data.hex_dump);

            // Clear the collection
            window.disChunks.reset();
               
            // Append the new chunks to the end of the list
            console.debug("refreshDisassembly, append new chunks %d",data.chunks.length);
            for (var i = 0; i < data.chunks.length; i++) 
            {
                var chunk = new DisChunkInfo({ 
                    sec_name : data.chunks[i].sec_name,
                    startOffset : data.chunks[i].startOffset,
                    endOffset : data.chunks[i].endOffset,
                    lines : data.chunks[i].lines,
                    hex_dump : data.chunks[i].lines,
                    isBoundary : data.chunks[i].isBoundary
                });
                window.disChunks.push(chunk);    
            }
        }
        
        // Recenter the Scrollbar
        scrollToAddr(offset);
     
        loadPopovers();
     
     
    }).fail(function(){
        alert('fail');
    });
                    
}

function updateDisassembly(offset)
{
    console.debug("updateDisassembly, start");

    var chunks = window.disChunks;

    // Map the offset to a chunk
    var index = getChunkIndex(offset);
    console.debug("updateDisassembly, got chunk index %d", index);

    if ( index == -1 )
    {
        // Need to load all new disassembly
        console.debug("updateDisassembly, refresh entire page");
        refreshDisassembly(offset);
        return true;
    }
    else
    {
        // Determine how many new chunks to request
        var mid_index = Math.floor((chunks.length/2));

        if ( index > mid_index )
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
    }
    
    return false;                
}


function getChunkIndex(offset)
{
    // Find the chunk that contains the address
    if ( "disChunks" in window )
    {
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
        
        var ch_name = chunks.models[index].get('sec_name');
        var ch_start = chunks.models[index].get('startOffset');
        var ch_end = chunks.models[index].get('endOffset');

        console.debug("Call partial: start %d, name %s\n",ch_start,ch_name);

        // Check if we can request more chunks
        if ( chunks.models[index].get('isBoundary') == false )
        {
            // Append new chunks to the bottom
            window.ignoreScrollEvents = true;
                        
            $.post('_partial_refresh', {id: window.disId, name:ch_name, start:ch_start, end:ch_end, count:chunk_count, dir:dir}).done(function(data){
                
                console.timeStamp("Received Response\n");

                // Determine the top most visible address
                var topAddr = getTopVisibleAssemblyAddr();
                console.debug("Partial Determine Top Visible %x",topAddr);

                // Update the chunk list
                if ( dir == 1 && data.chunks.length > 0 )
                {                                                                              
                    // Remove lower address chunks from the display
                    $('#listing').find("tbody:lt(" + data.chunks.length + ")").remove();
                    console.timeStamp("Remove %d chunks\n",data.chunks.length);

                    // Append the new listing
                    $('#listing tbody:last').after(data.disassembly);
                                        
                    // Scroll back to the original address
                    scrollToAddr(topAddr);                            
                    console.debug("Partial SCrollto %x",topAddr)
                    
                    // Remove the lowest chunks from the chunk list
                    for (var i = 0; i < data.chunks.length; i++) 
                    {
                        window.disChunks.shift();    
                    }   
                    
                    // Append the new chunks to the end of the list
                    for (var i = 0; i < data.chunks.length; i++) 
                    {
                        var chunk = new DisChunkInfo({ 
                            sec_name : data.chunks[i].sec_name,
                            startOffset : data.chunks[i].startOffset,
                            endOffset : data.chunks[i].endOffset,
                            lines : data.chunks[i].lines,
                            isBoundary : data.chunks[i].isBoundary
                        });
                        window.disChunks.push(chunk);    
                    }
                }
                if ( dir == 0 && data.chunks.length > 0 )
                {                    
                    // Remove higher address chunks from the display
                    var chunks_len = window.disChunks.length-data.chunks.length;
                    $('#listing').find("tbody:gt(" + (chunks_len-1) + ")").remove();

                    // Prepend the new listing
                    $('#listing tbody:first').before(data.disassembly);

                    // Scroll back to the original topmost address
                    scrollToAddr(topAddr);                            
                    console.debug("Partial SCrollto %x",topAddr)
                    
                    // Remove the highest chunks from the chunk list
                    for (var i = 0; i < data.chunks.length; i++) 
                    {
                        window.disChunks.pop();    
                    }   
                    
                    // Append the new chunks to the beginning of the list
                    var i = data.chunks.length;
                    while (i > 0)
                    {
                        var chunk = new DisChunkInfo({ 
                            sec_name : data.chunks[i-1].sec_name,
                            startOffset : data.chunks[i-1].startOffset,
                            endOffset : data.chunks[i-1].endOffset,
                            lines : data.chunks[i-1].lines,
                            isBoundary : data.chunks[i-1].isBoundary

                        });
                        window.disChunks.unshift(chunk);    
                        i = i-1;
                    }        
                }   

                loadPopovers();
                                
                console.timeStamp("Done Processing\n");
                
                window.scrollTimer = null;
                window.ignoreScrollEvents = false;                    
                  
            });                     
            
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
    var main_contain_left = $("#view")[0].offsetLeft;
    var main_contain_top = $("#view")[0].offsetTop;
    var view_padding_left = 16;
    var content_top = $("#myTabContent")[0].offsetTop;

    console.debug("getTopVisibleAssemblyRow main_left %d, main_top %d",
        main_contain_left, main_contain_top);
    
    // Calculate the first pixel of the top-most visible disassembly line
    var target_top = main_contain_top + content_top + 1;
    
    // Calculate the left most pixel of the top-most visible disassembly line
    var target_left = main_contain_left + view_padding_left + 1;
    
    // Get the Line of disassembly to determine the corresponding address
    var elem = myElementFromPoint(target_left, target_top);

    if ( elem.tagName.toLowerCase() != 'tr' )
    { 
        // Most likely in an internal tag (tr.branchlines, etc)
        elem = $(elem).closest('tr')[0];
    } 

    return elem;    
}

function getTopVisibleAssemblyAddr()
{
    var elem = getTopVisibleAssemblyRow();
    var intOffset = -1;
    if (elem) { 
        intOffset = parseInt(elem.getAttribute("addr"),16);
    }
    
    return intOffset;
}


function assemblyScrollHandler() 
{
    console.debug("assemblyScrollHandler, start");
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

        console.debug("assemblyScrollHandler, updating slider to 0x%x", elem.getAttribute("addr"));
        updateSlider(intOffset);

        // Load Code if necessary
        if ( !updateDisassembly(intOffset) )
        {
            window.scrollTimer=null;
        }
    } 
    else
    {
        console.debug("ScrollHandler: No addr in row")
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
        console.debug("assemblyScrollStopHandler, updating slider to 0x%x", offsetStr);
        updateSlider(intOffset);

        // Update the URL
    	router.navigate("view/"+url_hash_params.tab + "/offset/" + url_hash_params.offset);    	
    }
}

// update slider position via non-slider events (i.e., via scrollBar)
function updateSlider(addr) {
    //updateAddrDisplay(addr);
    $("#slider").slider("value", addr);
}


