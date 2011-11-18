package com.reverbin.ODA.shared;


import java.io.Serializable;

@SuppressWarnings("serial")
public class Instruction implements Serializable{

	public Instruction() {

	}
	
	
	public String opcode;
	public String registers;
	public String hexdata;
	public int address;
	public String addressFmt;
	public String comment;
	public String label;
	public String section;
	public int targetAddr;
	public InstructionType instrType;
}
