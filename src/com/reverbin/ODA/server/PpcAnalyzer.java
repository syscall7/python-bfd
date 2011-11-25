package com.reverbin.ODA.server;

import java.util.HashSet;
import java.util.regex.Pattern;


public class PpcAnalyzer extends ArchAnalyzer {
	
	public PpcAnalyzer(){
		
		// Initialize the opcode pattern for this architecture
		opcodePattern = Pattern.compile("(\\w+)(\\s+(.+))?");
		
		// Add all of the branch instructions
		this.branchInstructions = new HashSet<String>();
		this.callInstructions = new HashSet<String>();

	}
		
}