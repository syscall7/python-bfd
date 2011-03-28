package com.reverbin.ODA.server;

import java.io.*;
import java.util.regex.*;
import com.reverbin.ODA.shared.PlatformDescriptor;

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
            BufferedReader input = new BufferedReader(
                new InputStreamReader(p.getInputStream()));

            while ((line = input.readLine()) != null)
            {
                output += line + "\n";
            }
            input.close();
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
        	/*
            System.out.printf("Found %d matches", matcher.groupCount());
            for (int i = 0; i <= matcher.groupCount(); i++)
                System.out.println("'" + matcher.group(i) + "'");
            */
        	
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
	public static String dis(PlatformDescriptor platform, byte[] binary)
	{
		String listing = "";
		
		try 
		{
		    // create temp file
		    File temp = File.createTempFile("pattern", ".suffix");

		    // write to temp file
		    FileOutputStream out = new FileOutputStream(temp);
		    out.write(binary);
		    out.close();
		    
		    listing = exec(buildExecStr(platform, temp.getAbsolutePath()));
		    
		}
		catch (IOException e)
		{
		}
		
		if (listing.length() == 0)
		{
			return listing;
		}
		
		return dis2html(listing);
	}
}