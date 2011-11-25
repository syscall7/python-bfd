package com.reverbin.ODA.server;


import java.io.Serializable;


@SuppressWarnings("serial")
public class Instruction implements Serializable{

	public Instruction() {
		isTargetAddrValid = false;
		isError = false;
		instrType = InstructionType.NOP;
	}
	
	public boolean isError;
	public String errorType;
	public String rawInstrStr;
	public String opcode;
	public String registers;
	public String hexdata;
	public int address;
	public String comment;
	public String label;
	public String section;
	public int targetAddr;
	public boolean isTargetAddrValid;
	public InstructionType instrType;
}
