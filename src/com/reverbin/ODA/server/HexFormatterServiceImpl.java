package com.reverbin.ODA.server;

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
	    
		return new FormattedOutput(builder.toString(), Objdump.dis(platform, hex));
	}
}
