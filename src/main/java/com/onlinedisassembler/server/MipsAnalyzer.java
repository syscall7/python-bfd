package com.onlinedisassembler.server;

import java.util.HashSet;
import java.util.regex.Pattern;


public class MipsAnalyzer extends ArchAnalyzer {
	
	public MipsAnalyzer(){
		
		// Initialize the opcode pattern for this architecture
		opcodePattern = Pattern.compile("(\\w+)(\\s+(.+))?");
		
		// Add all of the branch instructions
		this.branchInstructions = new HashSet<String>();
		this.branchInstructions.add("beq");
		this.branchInstructions.add("bne");
		this.branchInstructions.add("blt");
		this.branchInstructions.add("bgt");
		this.branchInstructions.add("ble");
		this.branchInstructions.add("bge");
		this.branchInstructions.add("j");
		this.branchInstructions.add("jal");

		this.callInstructions = new HashSet<String>();

	}
		
}