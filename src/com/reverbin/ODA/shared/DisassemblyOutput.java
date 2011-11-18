package com.reverbin.ODA.shared;

import java.io.Serializable;
import java.util.HashMap;
import java.util.HashSet;

@SuppressWarnings("serial")
public class DisassemblyOutput implements Serializable {
	
	public DisassemblyOutput() {
		this.setFormattedAssembly("");
		this.instructionMap = new HashMap<Integer, Instruction>();
		this.stringList = new HashSet<String>();
	}
	
	public DisassemblyOutput(String assembly) {
		this.setFormattedAssembly(assembly);
		this.instructionMap = new HashMap<Integer, Instruction>();
		this.stringList = new HashSet<String>();
	}

	public void setFormattedAssembly(String formattedAssembly) {
		this.formattedAssembly = formattedAssembly;
	}

	public String getFormattedAssembly() {
		return formattedAssembly;
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

	public Instruction getInstruction(int addr) {
		return instructionMap.get(addr);
	}
	
	public HashMap<Integer, Instruction> getInstructions() {
		return this.instructionMap;
	}
	
	public void addInstruction(int addr, Instruction instr){
		instructionMap.put(addr,instr);
	}
	
	public void addString(String string){
		stringList.add(string);
	}
	
	public HashSet<String> getStrings()
	{
		return stringList;
	}
	
	private int totalLines;
	private int currentLines;
	private String formattedAssembly;
	private ObjectType objectType; 
    private HashSet<String> stringList;
	private HashMap<Integer, Instruction> instructionMap;

 
}
