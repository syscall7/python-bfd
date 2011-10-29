package com.reverbin.ODA.shared;

public enum Endian {
	BIG, LITTLE, DEFAULT;
	
	public static String getName(Endian e)
	{
		switch (e)
		{
			case BIG:		return "BIG";
			case LITTLE:	return "LITTLE";
			case DEFAULT:	return "DEFAULT";
			default:		break;
		}
		
		return "NONE";
	}
	
	public static Endian getEndian(String s)
	{
		if (s.equals("BIG"))
			return BIG;
		else if (s.equals("LITTLE"))
			return LITTLE;
		else
			return DEFAULT;
	}
}
