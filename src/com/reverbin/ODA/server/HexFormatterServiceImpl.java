package com.reverbin.ODA.server;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

import com.reverbin.ODA.client.HexFormatterService;
import com.reverbin.ODA.shared.*;
import com.google.gwt.user.server.rpc.RemoteServiceServlet;

@SuppressWarnings("serial")
public class HexFormatterServiceImpl extends RemoteServiceServlet implements HexFormatterService {

	@Override
	public FormattedOutput formatHex(PlatformDescriptor platform, byte[] hex) throws IllegalArgumentException {
		final String HEXES = "0123456789ABCDEF";
		final StringBuilder builder = new StringBuilder(2 * hex.length);

		for ( final byte b : hex ) {
	    	builder.append(HEXES.charAt((b & 0xF0) >> 4))
	         .append(HEXES.charAt((b & 0x0F)))
	         .append(" ");
	    }
		
	    // create temp file
	    File temp = null;
    
		try 
		{
		    // create temp file
		    temp = File.createTempFile("pattern", ".suffix");

		    // write to temp file
		    FileOutputStream out = new FileOutputStream(temp);
		    out.write(hex);
		    out.close();
	    
		}
		catch (IOException e)
		{
		}
	    
		
	    String asm = Objdump.dis(platform, temp.getAbsolutePath());
	    String strings = Strings.strings(temp.getAbsolutePath());
	    
		return new FormattedOutput(builder.toString(), asm, strings);
	}
}
