var oda = oda || {};

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
            window.activeTab = tab;
            if ( tab == 'tab-assembly' || tab == 'tab-hexdump' )
            {
                scrollToAddr(window.lastAddr);
            }
            var tabselector = '[data-toggle="tab"][href="#' + tab + '"]'; 
            $(tabselector).tab('show');
		},
		tab : function(tab,offset) {
		    window.activeTab = tab;
            var tabselector = '[data-toggle="tab"][href="#' + tab + '"]'; 
            $(tabselector).tab('show');
			if ( tab == 'tab-assembly' || tab == 'tab-hexdump' )
			{
			    // Only process tabs for existing sessions
			    //   In other words, you can't navigate to an address
			    //   by typing in the URL if you haven't already started
			    //   a session
			    if (typeof window.disId === "undefined") 
			    {
			        // Save the initial offset for use by the Load function
			        window.initialOffset = parseInt(offset,16);
			    }
			    else
			    {
    				var assembly_position = window.assembly_position; 
    
    				// Select the assembly tab
    				var tabselector = '#' + tab;
    			    $(tabselector).tab('show');
    				
    				// Check if the target offset is currently loaded in the browser
    				var intOffset = parseInt(offset,16);
                    if ( !updateDisplayedFileContent(intOffset,false) )
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
	window.lastAddr = 0;
	
	router = new WorkspaceRouter();
	Backbone.history.start();
	

	$('#myTabContent').bind('scrollstop', scrollStopHandler);
    $('#myTabContent').bind('scroll', function(event) {
            if ( window.scrollTimer == null )
            {
                window.scrollTimer = setTimeout(scrollHandler, 100);
            }
        });
        
    // Use a timer for dynamic sizing for performance reasons 

	$('a[data-toggle="tab"]').on('shown', function(e) {
		
		// Don't navigate to tabs that are already showing
        var t = $(e.target).attr('href').replace('#','')
		if( window.location.hash.indexOf( t ) == -1 )
		{
            router.navigate("view/" + t);
	    } 
	})

});


function intToHexStr(offset)
{
    return ("000000000000000" + offset.toString(16)).substr(-8);    
}


function scrollToAddr(offset)
{
    // go back up to 16 bytes
    var tries = 16;

    while (offset > 0 && tries > 0) {
        // Convert to a hex string with leading zeroes
        var hexStr = intToHexStr(offset);

        // Scroll to the proper offset in the disassembly
        var offsetselector = '#' + window.activeTab + ' tr[addr=' + hexStr + ']';
        var offset_element = $(offsetselector);

        // Check if element exists
        if ( offset_element.length > 0 )
        {
            var disoffset_top = offset_element[0].offsetTop;

            // Row element offset doesn't include size of the download bar
            $('#myTabContent').scrollTop(disoffset_top + 1);
            window.lastAddr = offset;
            updateSlider(offset);
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
        placement: 'right',
        delay: { show: 1000, hide: 100 },
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
function refreshDisassembly(offset, show_loading)
{
    if ( show_loading) {
        $('#loading-panel').show();
    }
    $('#assembly-scroll').hide();

    $.post('_refresh', {id: window.disId, addr:offset}).done(function(data){

        // Append new chunks to the bottom
        window.ignoreScrollEvents = true;

        // Update the chunk list
        if ( data.chunks.length > 0 )
        {
            // Remove old chunks from the display
            $('#listing').find("tbody").remove();

            // Append the new listing
            $('#listing').find("colgroup").after(data.disassembly);

            // Clear the collection
            window.disChunks.reset();
               
            // Append the new chunks to the end of the list
            appendChunks(window.disChunks, data.chunks);

        }
        $('#assembly-scroll').show();
        $('#loading-panel').hide();
        
        // Recenter the Scrollbar
        scrollToAddr(offset);

        loadPopovers();
        
        window.scrollTimer = null;
        window.ignoreScrollEvents = false;                    

    }).fail(function(){
        oda.alert('refresh failed');
    });
                    
}

function updateDisplayedFileContent(offset,isScroll)
{
    // Get the proper chunks depending on which tab is displayed
    if ( window.activeTab == 'tab-hexdump')
    {
        var chunks = window.hexChunks;        
    }
    else
    {
        var chunks = window.disChunks;
    }

    // Map the offset to a chunk
    var index = getChunkIndex(offset,chunks);
    if ( index == -1 )
    {
        // Need to load all new content
        if ( window.activeTab == 'tab-hexdump')
        {
            refreshHex(offset,true);        
        }
        else
        {
            refreshDisassembly(offset,true);
        }
        return true;
    }
    else
    {
        // Determine how many new chunks to request
        var mid_index = Math.floor((chunks.length/2));

        if ( index > mid_index )
        {
            // Partial load
            var requested_chunks = index-mid_index;
            if ( window.activeTab == 'tab-hexdump')
            {
                return loadPartialHex(1,requested_chunks,offset,isScroll);        
            }
            else
            {
                return requestMoreDisassembly(1,requested_chunks,offset,isScroll);
            }
            
        }
        else if ( index < mid_index )
        {
            // Partial load
            var requested_chunks = mid_index - index;
            if ( window.activeTab == 'tab-hexdump')
            {
                return loadPartialHex(0,requested_chunks,offset,isScroll);        
            }
            else
            {
                return requestMoreDisassembly(0,requested_chunks,offset,isScroll);        
            }
        }
    }
    
    return false;                
}


function getChunkIndex(offset,chunks)
{
    // Find the chunk that contains the address
    if ( "disChunks" in window )
    {
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


function prependChunks(chunks,newChunks)
{
    // Remove the chunks with the highest address
    for (var i = 0; i < newChunks.length; i++) 
    {
        chunks.pop();    
    }   

    // Prepend the new chunks
    var i = newChunks.length;
    while (i > 0)
    {
        var chunk = new DisChunkInfo({ 
            startOffset : newChunks[i-1].startOffset,
            endOffset : newChunks[i-1].endOffset,
            isBoundary : newChunks[i-1].isBoundary
        });
        chunks.unshift(chunk);    
        i = i-1;
    }            
}


function appendChunks(chunks,newChunks)
{
    // Remove the chunks with the lowest address
    for (var i = 0; i < newChunks.length; i++) 
    {
        chunks.shift();    
    }   
    
    // Append the new chunks
    for (var i = 0; i < newChunks.length; i++) 
    {
        var chunk = new DisChunkInfo({ 
            startOffset : newChunks[i].startOffset,
            endOffset : newChunks[i].endOffset,
            isBoundary : newChunks[i].isBoundary
        });
        chunks.push(chunk);    
    }
}

function requestMoreDisassembly(dir,chunk_count,offset,isScroll)
{
    var chunks = window.disChunks;
    if ( chunk_count < chunks.length )
    {
        // Keeping some of the existing window
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
        
        var ch_start = chunks.models[index].get('startOffset');
        var ch_end = chunks.models[index].get('endOffset');

        // Check if we can request more chunks
        if ( chunks.models[index].get('isBoundary') == false )
        {
            // Append new chunks to the bottom
            window.ignoreScrollEvents = true;
                        
            $.post('_partial_refresh', {id: window.disId, start:ch_start, end:ch_end, count:chunk_count, dir:dir}).done(function(data){
                
                if ( isScroll )
                {
                    // Scroll to the top most visible address after load
                    var scrollAddr = getTopVisibleAssemblyAddr();
                }
                else
                {
                    // Scroll to the provided address
                    var scrollAddr = offset;
                }
                
                // Update the chunk list
                if ( dir == 1 && data.chunks.length > 0 )
                {                                                                              
                    // Remove lower address chunks from the display
                    $('#listing').find("tbody:lt(" + data.chunks.length + ")").remove();

                    // Append the new listing
                    $('#listing tbody:last').after(data.disassembly);
                                        
                    // Scroll back to the original address
                    scrollToAddr(scrollAddr);                            
                                        
                    // Append the new chunks to the end of the list
                    appendChunks(chunks, data.chunks);
                }
                if ( dir == 0 && data.chunks.length > 0 )
                {                    
                    // Remove higher address chunks from the display
                    var chunks_len = chunks.length-data.chunks.length;
                    $('#listing').find("tbody:gt(" + (chunks_len-1) + ")").remove();

                    // Prepend the new listing
                    $('#listing tbody:first').before(data.disassembly);

                    // Scroll back to the original topmost address
                    scrollToAddr(scrollAddr);                            
                                        
                    // Append the new chunks to the beginning of the list
                    prependChunks(chunks, data.chunks);
                }   

                loadPopovers();
                                
                window.scrollTimer = null;
                window.ignoreScrollEvents = false;                    
                  
            });                     
            
            return true;            
        }
        else
        {

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

function isScrollableTab(tab)
{
    if ( tab == 'tab-assembly' )
    {
        return true;
    }
    else if (tab == 'tab-hexdump' )
    {
        return true;
    }
    
    return false;
}


function scrollHandler() 
{
    if (window.ignoreScrollEvents)
    {
        window.scrollTimer=null;
        return;
    }

    if ( !isScrollableTab(window.activeTab) )
    {
        window.scrollTimer=null;
        return;
    }

    var elem = getTopVisibleAssemblyRow();
    if (elem) { 
        var intOffset = parseInt(elem.getAttribute("addr"),16);

        updateSlider(intOffset);

        // Load Code if necessary
        if ( !updateDisplayedFileContent(intOffset,true) )
        {
            window.scrollTimer=null;
        }
    } 
    else
    {
        window.scrollTimer=null;
    }
}

function scrollStopHandler() 
{
    if (window.ignoreScrollEvents)
    {
        return;
    }
    
    if ( !isScrollableTab(window.activeTab) )
    {
        return;
    }

	var elem = getTopVisibleAssemblyRow();
	
	if (elem) { 
        var url_hash_params = {};
        var offsetStr = elem.getAttribute("addr");
        url_hash_params.tab = window.activeTab;
		url_hash_params.offset = offsetStr;

        var intOffset = parseInt(offsetStr,16);
        updateSlider(intOffset);
        window.lastAddr = intOffset;

        // Update the URL
    	router.navigate("view/"+url_hash_params.tab + "/offset/" + url_hash_params.offset);    	
    }
}

// update slider position via non-slider events (i.e., via scrollBar)
function updateSlider(addr) {
    //updateAddrDisplay(addr);
    $("#slider").slider("value", addr);
}


