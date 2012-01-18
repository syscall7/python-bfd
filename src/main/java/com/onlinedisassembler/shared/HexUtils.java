package com.onlinedisassembler.shared;

public class HexUtils {
	public static byte[] textToBytes(String text)
	{
		char[] hex = text.replaceAll("\\s", "").toCharArray();
		int length = hex.length / 2;
	    byte[] bytes = new byte[length];
	    for (int i = 0; i < length; i++) 
	    {
	      int high = Character.digit(hex[i * 2], 16);
	      int low = Character.digit(hex[i * 2 + 1], 16);
	      int value = (high << 4) | low;
	      if (value > 127)
	        value -= 256;
	      bytes[i] = (byte) value;
	    }
	    
	    return bytes;
	}
	
	public static String bytesToText(byte[] bytes)
	{
		final String HEXES = "0123456789ABCDEF";
		final StringBuilder builder = new StringBuilder(2 * bytes.length);

		for ( final byte b : bytes ) {
	    	builder.append(HEXES.charAt((b & 0xF0) >> 4))
	         .append(HEXES.charAt((b & 0x0F)))
	         .append(" ");
	    }
		
		return builder.toString();
	}
}
