package com.onlinedisassembler.shared;

public enum PlatformOption {
	THUMB, DEFAULT, NONE;
	
	public static String getName(PlatformOption e)
	{
		switch (e)
		{
			case THUMB: 		
				return "THUMB";
			case DEFAULT:		
				return "DEFAULT";
			case NONE:			
				return "NONE";

			default:			
				break;
		}
		
		return "NONE";
	}
	
	public static PlatformOption getPlatformOption(String s)
	{
		if (s.equals("THUMB"))
			return THUMB;
		else if (s.equals("DEFAULT"))
			return DEFAULT;
		else if (s.equals("NONE"))
			return NONE;
		else
			return DEFAULT;
	}
}