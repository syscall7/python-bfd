package com.reverbin.ODA.server;

import java.io.*;
import java.util.regex.*;

import com.reverbin.ODA.shared.DisassemblyOutput;
import com.reverbin.ODA.shared.Endian;
import com.reverbin.ODA.shared.PlatformDescriptor;
import com.reverbin.ODA.shared.PlatformId;

import org.apache.commons.io.*;

public class Objdump
{	
    /**
     * Execute the given command line and return the captured stdout
     */
    private static String exec(String cmdline)
    {   /* ### TODO: This should eventually be a StringBuilder class for
                     efficiency reasons
        */
        String output = "";
        try
        {
            String line;
            Process p = Runtime.getRuntime().exec(cmdline);
            output = IOUtils.toString(p.getInputStream(), "UTF-8");
        }
        catch (Exception err)
        {
            err.printStackTrace();
        }
        return output;
    }

    /**
     * Convert the disassembly listing to pretty HTML
     */
    private static DisassemblyOutput dis2html(String dis, int offset, int length)
    {
    	// ignore leading text
    	Pattern pattern = Pattern.compile("^\\s*[0-9a-fA-F]+:.*", Pattern.DOTALL | Pattern.MULTILINE);
        Matcher matcher = pattern.matcher(dis);
        matcher.find();
        dis = matcher.group();
        final int MAX_LINES = 2000;
        int line = 0;
        int count = 0;
        int totalCount = 0;
        DisassemblyOutput output = new DisassemblyOutput("");
        
        // now parse each line to get the offset, raw bytes and instruction
        pattern = Pattern.compile(
                    // beginning of the line plus white space
                    "^\\s*" +               
                    // offset and colon followed by white space
                    "([0-9a-f]*):\\s+" +    
                    // raw binary bytes "xxxxxxxx" or "xx xx xx .."
                    "([0-9a-f]{8}|(?:[0-9a-f]{2} )+)" +
                    // instruction
                    "(.*)$",
                    Pattern.MULTILINE);
        matcher = pattern.matcher(dis);
        
        StringBuffer sb = new StringBuffer(dis.length());
        
        /*
        StringBuffer offsets = new StringBuffer(dis.length());
        StringBuffer raw = new StringBuffer(dis.length());
        StringBuffer insns = new StringBuffer(dis.length());

        offsets.append("<td class=\"offset\">");
        raw.append("<td class=\"raw\">");
        insns.append("<td class=\"insn\">");
        */
        
        // for each match (each line, really)
        //while (matcher.find() && (count++ < MAX_LINES))
        while (matcher.find())
        {       	
        		
        	totalCount++;
        	
        	if (line++ < offset) {
        		continue;
        	}
        	
        	if (count < length)
        	{
        		/*
	        	offsets.append(String.format("%1$#6s\n", matcher.group(1)));
	        	raw.append(String.format("%1$-16s\n", matcher.group(2).replace(" ", "")));
	        	insns.append(String.format("%1$s\n", matcher.group(3).trim()));
	        	*/
        		
	        	/* offset (right justified), raw bytes (left just), instruction */
	            sb.append(String.format("<offset>%1$#6s </offset>" +
	            		                "<raw>%2$-16s </raw>" +
	            		                "<insn>%3$s\n</insn>", 
	            		matcher.group(1), matcher.group(2).replace(" ", ""), matcher.group(3).trim()));
	        	
	        	count++;
	        	
        	}	
        	

        	
        	/*
        	sb.append(String.format("%1$#6s %2$-16s %3$s\n", 
	                matcher.group(1), matcher.group(2).replace(" ", ""), matcher.group(3)));
        	*/
        	

        }

        /*
        offsets.append("</td>");
        raw.append("</td>");
        insns.append("</td>");
        */
        output.setTotalLines(totalCount);
        output.setCurrentLines(count);
        //output.setFormattedAssembly("<table><tr>" + offsets.toString() +  raw.toString() + insns.toString() + "</tr></table>");
        output.setFormattedAssembly(sb.toString());
        		
        return output;
        
        //return "<pre>" + sb.toString() + "</pre>";
    }

    private static String buildExecStr(PlatformDescriptor platform, String filePath)
    {
    	//"objdump -D -b binary -m " + platform + " " + );
    	String prefix = "";
    	String machine = "";
    	
    	switch (platform.platformId)
    	{
	    	case PPC: {
	    		prefix = "/usr/local/bin/ppc-elf-";
	    		machine = "powerpc";
	    		break;
	    	}
	    	case X86: {
	    		prefix = "/usr/bin/";
	    		machine = "i386";
	    		break;
	    	}
	    	case ARM: {
	    		prefix = "/usr/local/bin/arm-elf-";
	    		machine = "arm";
	    		break;
	    	}
	    	case MIPS: {
	    		prefix = "/usr/local/bin/mips-elf-";
	    		machine = "mips";
	    		break;
	    	}
    	}
    	
    	String endian = "";
    	
    	switch (platform.endian)
    	{
    		case BIG:	endian = " -EB";		break;
    		case LITTLE:	endian = " -EL";	break;
    		case DEFAULT:	endian = "";	break;
    	}
    	
    	return  prefix + "objdump -D -b binary -m " + machine + " --adjust-vma=" + platform.baseAddress + endian + " " + filePath;
    }

    /**
     * Run objdump on the given binary data for the given platform
     * @param platform
     * @param binary
     * @return
     */
	public static DisassemblyOutput dis(PlatformDescriptor platform, String filePath, int offset, int length)
	{
		DisassemblyOutput output = new DisassemblyOutput("");
		String listing = "";  
		listing = exec(buildExecStr(platform, filePath));
		
		
		if (listing.length() == 0)
		{
			return output;
		}
		
		return dis2html(listing, offset, length);
	}
}