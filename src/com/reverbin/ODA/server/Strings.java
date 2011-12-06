package com.reverbin.ODA.server;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Strings {
    /**
     * Execute the given command line and return the captured stdout
     */
    private static String exec(String cmdline)
    {   /* ### TODO: This should eventually be a StringBuilder class for
                     efficiency reasons
        */
        String output = "";
        boolean noStringsFound = true;
        try
        {
            String line;
            Process p = Runtime.getRuntime().exec(cmdline);
            BufferedReader input = new BufferedReader(
                new InputStreamReader(p.getInputStream()));
            
            // now parse each line to get the offset, raw bytes and instruction
            Pattern pattern = Pattern.compile(
                        // beginning of the line plus white space
                        "^\\s*" +               
                        // offset followed by white space
                        "([0-9a-f]*)\\s+" +    
                        // string
                        "(.*)");

            while ((line = input.readLine()) != null)
            {
            	Matcher matcher = pattern.matcher(line);
            	matcher.find();
            	output += String.format("<offset>%1$#6s </offset>" +
		                "<insn>%2$-16s\n</insn>",
		                matcher.group(1), matcher.group(2).replace("<", "&lt").replace(">", "&gt"));
            	noStringsFound = false;
            }
            input.close();
        }
        catch (Exception err)
        {
            err.printStackTrace();
        }
        if (noStringsFound)
        	output = "<insn>No strings found</insn>";
        return output;
    }
    
	public static String strings(String filePath)
	{
		return exec("strings -t x " + filePath);
	}
}
