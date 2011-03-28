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
            	output += String.format("<span class=\"offset\">%1$#6s </span>" +
		                "<span class=\"insn\">%2$-16s </span>\n",
		                matcher.group(1), matcher.group(2));
            }
            input.close();
        }
        catch (Exception err)
        {
            err.printStackTrace();
        }
        return output;
    }
    
	public static String strings(String filePath)
	{
		return "<pre>" + exec("strings -t x " + filePath) + "</pre>";
	}
}
