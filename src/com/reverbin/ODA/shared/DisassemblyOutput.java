package com.reverbin.ODA.shared;

import java.io.Serializable;
import java.util.HashMap;
import java.util.HashSet;

@SuppressWarnings("serial")
public class DisassemblyOutput implements Serializable {
	
	public DisassemblyOutput() {
	}
	
	public void setTotalLines(int l) {
		totalLines = l;
	}
	
	public int getTotalLines() {
		return totalLines;
	}
	
	public void setCurrentLines(int l) {
		currentLines = l;
	}
	
	public int getCurrentLines() {
		return currentLines;
	}
	
	public void setObjectType(ObjectType ot) {
		objectType = ot;
	}
	
	public ObjectType getObjectType() {
		return objectType;
	}
	
	public String getOffsetHtml()
	{
		return offsetHtml;
	}
	
	public void setOffsetHtml(String html)
	{
		offsetHtml = html;
	}

	public String getOpcodeHtml()
	{
		return opcodeHtml;
	}

	public void setOpcodeHtml(String html)
	{
		opcodeHtml = html;
	}

	public String getRawBytesHtml()
	{
		return rawBytesHtml;
	}	

	public void setRawBytesHtml(String html)
	{
		rawBytesHtml = html;
	}
	
	private String opcodeHtml;
	private String offsetHtml;
	private String rawBytesHtml;
	private int totalLines;
	private int currentLines;
	private ObjectType objectType;  
}
