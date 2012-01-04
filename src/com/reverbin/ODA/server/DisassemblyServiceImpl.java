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
		DisassemblyAnalyzer analyzer = new DisassemblyAnalyzer();
		String objDumpListing;
		String sectionListing;
		ObjectType objType;
		
		try 
		{
		    SimpleDateFormat sdfDate = new SimpleDateFormat("yyyyMMdd-HHmmss");

			file = new File(HostUtils.getUploadLogDir()+sdfDate.format(new Date()));
			file.createNewFile();

		    // write to temp file
		    FileOutputStream out = new FileOutputStream(file);
		    out.write(binary);
		    out.close();
	    
		}
		catch (IOException e)
		{
		}	

		if (binary[0] == 'M' && binary[1] == 'Z')
			objType = ObjectType.PE;
		else if (binary[0] == 0x7f && binary[1] == 'E' && binary[2] == 'L' && binary[3] == 'F')
			objType = ObjectType.ELF;
		else {
			objType = ObjectType.BINARY;
		}
		
		objDumpListing = Objdump.dis(platformDesc, file.getAbsolutePath(), objType);
		analyzer.parseObjdumpListing(objDumpListing, offset, length, platformDesc);
		ret = analyzer.getDisassemblyOutput();
		
		ret.setObjectType(objType);
		
		if ((binary.length == 28) || (binary.length == 35))
		{
			file.delete();
		}
		
		// Get Section Data for Elf files
		if ( objType == ObjectType.ELF )
		{
			sectionListing = Objdump.getSections(file.getAbsolutePath(), platformDesc);
			ret.setSectionHtml(analyzer.parseSectionData(sectionListing));
			ret.setSections(analyzer.getSections());
		}
		else
		{
			ret.setSectionHtml("<insn>No sections found</insn>");
		}
		
		// Get String Data
		String strings = Strings.strings(file.getAbsolutePath());
		ret.setStringHtml(strings);
		
		return ret;
	}

//	public String getStrings() throws IllegalArgumentException {
//		
//	    // create temp file
//	    File temp = null;
//    
//		try 
//		{
//		    // create temp file
//		    temp = File.createTempFile("pattern", ".suffix");
//
//		    // write to temp file
//		    FileOutputStream out = new FileOutputStream(temp);
//		    out.write(binary);
//		    out.close();
//	    
//		}
//		catch (IOException e)
//		{
//		}
//	    
//	    String strings = Strings.strings(temp.getAbsolutePath());
//	    
//		return strings;
//	}
	
	
}
