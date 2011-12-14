package com.onlinedisassembler.server;

/**
 * Utility class for abstracting the server host machine type
 *
 */
public class HostUtils 
{
	/**
	 * Check if we're running on a windows host
	 * @return
	 */
	public static boolean isWindows()
	{	 
		String os = System.getProperty("os.name").toLowerCase();
	    return (os.indexOf( "win" ) >= 0); 
	}
	
	public static String getUploadLogDir()
	{	 
		if ( isWindows() )
		{
			return "C:/var/log/oda/";
		}
		else
		{
			return "/var/log/oda/";
		}
	}
	
	public static String getBinutilsDir()
	{
		if ( isWindows() )
		{
			return "C:/cross-tools/binutils-builds/bin/";
		}
		else
		{
			return "/usr/local/bin/";
		}			
	}
	
}
