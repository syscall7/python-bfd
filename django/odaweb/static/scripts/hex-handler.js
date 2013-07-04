
// Load an entire new page of hex
function refreshHex(offset,scrollto)
{
    $.post('_refreshHex', {id: window.disId, addr:offset}).done(function(data){

        // Update the chunk list
        if ( data.chunks.length > 0 )
        {
            // Remove old chunks from the display
            $('#hex-dump-table').find("tbody").remove();

            // Append the new listing
            $('#hex-dump-table').append(data.hex_dump);

            // Clear the collection
            window.hexChunks.reset();
               
            // Append the new chunks to the end of the list
            appendChunks(window.hexChunks,data.chunks);
        }
                
        // TODO: Port to Hex display
        //$('#hex-scroll').show();
        //$('#loading-panel').hide();
        
        // Recenter the Scrollbar
        if ( scrollto )
        {
            scrollToAddr(offset);
        }
        
        window.scrollTimer = null;
        window.ignoreScrollEvents = false;                    

    }).fail(function(){
        alert('fail');
    });
                    
}


function loadPartialHex(dir,chunk_count,offset,isScroll)
{
    var chunks = window.hexChunks;
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
                        
            $.post('_partial_refreshHex', {id: window.disId, start:ch_start, end:ch_end, count:chunk_count, dir:dir}).done(function(data){
                
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
                    $('#hex-dump-table').find("tbody:lt(" + data.chunks.length + ")").remove();

                    // Append the new listing
                    $('#hex-dump-table tbody:last').after(data.hex_dump);
                                        
                    // Scroll back to the original address
                    scrollToAddr(scrollAddr);                            
                                        
                    // Append the new chunks to the end of the list
                    appendChunks(chunks, data.chunks);
                }
                if ( dir == 0 && data.chunks.length > 0 )
                {                    
                    // Remove higher address chunks from the display
                    var chunks_len = chunks.length-data.chunks.length;
                    $('#hex-dump-table').find("tbody:gt(" + (chunks_len-1) + ")").remove();

                    // Prepend the new listing
                    $('#hex-dump-table tbody:first').before(data.hex_dump);

                    // Scroll back to the original topmost address
                    scrollToAddr(scrollAddr);                            
                                        
                    // Append the new chunks to the beginning of the list
                    prependChunks(chunks, data.chunks);
                }   
                                
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



