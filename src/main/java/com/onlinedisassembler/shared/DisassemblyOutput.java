package com.onlinedisassembler.shared;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Collection;
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

	public String getSectionHtml()
	{
		return sectionHtml;
	}	

	public void setSectionHtml(String html)
	{
		sectionHtml = html;
	}

	public void setAddrToLineMap(HashMap<Integer, Integer> map)
	{
		addrToLineMap = map;
	}
	
	public HashMap<Integer, Integer> getAddrToLineMap()
	{
		return addrToLineMap;
	}
	
	public void setBranchTargetHtml(String html)
	{
		branchTargetHtml = html;
	}
	
	public String getBranchTargetHtml()
	{
		return branchTargetHtml;
	}
	
	public void setStringHtml(String html)
	{
		stringHtml = html;
	}
	
	public String getStringHtml()
	{
		return stringHtml;
	}
	
	public void setHexDump(String hd)
	{
		hexDump = hd;
	}
	
	public String getHexDump()
	{
		return hexDump;
	}

	public HashMap<Integer, CodeSection> getSections()
	{
		return sections;
	}
	
	public void setSections(HashMap<Integer, CodeSection> s)
	{
		sections = s;
	}
	
	private String opcodeHtml;
	private String offsetHtml;
	private String rawBytesHtml;
	private String sectionHtml;
	private String stringHtml;
	private int totalLines;
	private int currentLines;
	private ObjectType objectType;
	private HashMap<Integer, Integer> addrToLineMap;
	private String branchTargetHtml;
	private String hexDump;
	private HashMap<Integer, CodeSection> sections;
}
