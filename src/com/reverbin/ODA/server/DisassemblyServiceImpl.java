package com.reverbin.ODA.server;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

import com.reverbin.ODA.client.DisassemblyService;
import com.reverbin.ODA.shared.*;
import com.google.gwt.user.server.rpc.RemoteServiceServlet;

@SuppressWarnings("serial")
public class DisassemblyServiceImpl extends RemoteServiceServlet implements DisassemblyService {

	@Override
	public 	DisassemblyOutput disassemble(byte[] binary, PlatformDescriptor platformDesc) throws IllegalArgumentException {
		
	    // create temp file
	    File temp = null;
    
		try 
		{
		    // create temp file
		    temp = File.createTempFile("pattern", ".suffix");

		    // write to temp file
		    FileOutputStream out = new FileOutputStream(temp);
		    out.write(binary);
		    out.close();
	    
		}
		catch (IOException e)
		{
		}
	    
		
	    String asm = Objdump.dis(platformDesc, temp.getAbsolutePath());
	    String strings = "";
	    
		return new DisassemblyOutput("", asm, strings);
	}

	@Override
	public String strings(byte[] binary) throws IllegalArgumentException {
		
	    // create temp file
	    File temp = null;
    
		try 
		{
		    // create temp file
		    temp = File.createTempFile("pattern", ".suffix");

		    // write to temp file
		    FileOutputStream out = new FileOutputStream(temp);
		    out.write(binary);
		    out.close();
	    
		}
		catch (IOException e)
		{
		}
	    
	    String strings = Strings.strings(temp.getAbsolutePath());
	    
		return strings;
	}
}
