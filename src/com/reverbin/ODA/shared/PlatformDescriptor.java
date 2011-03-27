package com.reverbin.ODA.shared;

import java.io.Serializable;

@SuppressWarnings("serial")
public class PlatformDescriptor  implements Serializable {

	private String platformStr;
	
	public PlatformDescriptor()
	{
		platformStr = "not set";
	}
	
	public PlatformDescriptor(String p)
	{
		this.platformStr = p;
	}
	
	public String toString()
	{
		return this.platformStr;
	}
}
