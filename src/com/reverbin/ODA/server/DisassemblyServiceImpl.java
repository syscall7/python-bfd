package com.reverbin.ODA.server;
import java.text.SimpleDateFormat;
import java.util.Date;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

import com.reverbin.ODA.client.DisassemblyService;
import com.reverbin.ODA.shared.*;
import com.google.gwt.user.server.rpc.RemoteServiceServlet;

@SuppressWarnings("serial")
public class DisassemblyServiceImpl extends RemoteServiceServlet implements DisassemblyService {

	@Override
	public 	DisassemblyOutput disassemble(byte[] binary, PlatformDescriptor platformDesc, int offset, int length) throws IllegalArgumentException {
		
		File file = null;
		DisassemblyOutput ret = null;
		try 
		{
		    SimpleDateFormat sdfDate = new SimpleDateFormat("yyyyMMdd-HHmmss");

			file = new File("/var/log/oda/"+sdfDate.format(new Date()));
			file.createNewFile();

		    // write to temp file
		    FileOutputStream out = new FileOutputStream(file);
		    out.write(binary);
		    out.close();
	    
		}
		catch (IOException e)
		{
		}
	    
	    
		ret = Objdump.dis(platformDesc, file.getAbsolutePath(), offset, length);
		
		if (binary[0] == 'M' && binary[1] == 'Z')
			ret.setObjectType(ObjectType.PE);
		else if (binary[0] == 0x7f && binary[1] == 'E' && binary[2] == 'L' && binary[3] == 'F')
			ret.setObjectType(ObjectType.ELF);
		else {
			ret.setObjectType(ObjectType.BINARY);
		}
		
		if ((binary.length == 28) || (binary.length == 35))
		{
			file.delete();
		}
		
		return ret;
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
