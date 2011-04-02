package com.reverbin.ODA.server;

import java.io.*;
import java.util.regex.*;
import com.reverbin.ODA.shared.PlatformDescriptor;
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
    private static String dis2html(String dis)
    {
    	// ignore leading text
    	Pattern pattern = Pattern.compile("^\\s+?0:.*", Pattern.DOTALL | Pattern.MULTILINE);
        Matcher matcher = pattern.matcher(dis);
        matcher.find();
        dis = matcher.group();
        
        // now parse each line to get the offset, raw bytes and instruction
        pattern = Pattern.compile(
                    // beginning of the line plus white space
                    "^\\s*" +               
                    // offset and colon followed by white space
                    "([0-9a-f]*):\\s+" +    
                    // raw binary bytes "xxxxxxxx" or "xx xx xx .."
                    "([0-9a-f]{8}|(?:[0-9a-f]{2} )+)\\s+" +
                    // instruction
                    "(.*)$",
                    Pattern.MULTILINE);
        matcher = pattern.matcher(dis);
        StringBuffer sb = new StringBuffer(dis.length());

        // for each match (each line, really)
        while (matcher.find())
        {       	
        	/* offset (right justified), raw bytes (left just), instruction */
            sb.append(String.format("<span class=\"offset\">%1$#6s </span>" +
            		                "<span class=\"raw\">%2$-16s </span>" +
            		                "<span class=\"insn\">%3$s</span>\n", 
            		matcher.group(1), matcher.group(2).replace(" ", ""), matcher.group(3)));
        }

        return "<pre>" + sb.toString() + "</pre>";
    }

    private static String buildExecStr(PlatformDescriptor platform, String filePath)
    {
    	//"objdump -D -b binary -m " + platform + " " + );
    	String prefix = "";
    	String machine = "";
    	
    	if (platform.toString().equals("PowerPC"))
    	{
    		prefix = "/usr/local/bin/ppc-elf-";
    		machine = "powerpc";
    	}
    	else if (platform.toString().equals("x86"))
    	{
    		prefix = "/usr/bin/";
    		machine = "i386";
    	}
    	else if (platform.toString().equals("ARM"))
    	{
    		prefix = "/usr/local/bin/arm-elf-";
    		machine = "arm";
    	}
    	else if (platform.toString().equals("MIPS"))
    	{
    		prefix = "/usr/local/bin/mips-elf-";
    		machine = "mips";
    	}
    	
    	return  prefix + "objdump -D -b binary -m " + machine + " " + filePath;
    }

    /**
     * Run objdump on the given binary data for the given platform
     * @param platform
     * @param binary
     * @return
     */
	public static String dis(PlatformDescriptor platform, String filePath)
	{
		String listing = "";  
		listing = exec(buildExecStr(platform, filePath));
		
		if (listing.length() == 0)
		{
			return listing;
		}
		
		return dis2html(listing);
	}
}