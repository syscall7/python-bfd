package com.reverbin.ODA.server;

import java.util.HashSet;
import java.util.regex.Pattern;


public class x86Analyzer extends ArchAnalyzer {
	
	public x86Analyzer(){
		
		// Initialize the opcode pattern for this architecture
		opcodePattern = Pattern.compile("(\\w+)(\\s+(.+))?");
		
		// Add all of the branch instructions
		this.branchInstructions = new HashSet<String>();
		this.branchInstructions.add("jne");
		this.branchInstructions.add("jo");
		this.branchInstructions.add("jno");
		this.branchInstructions.add("js");
		this.branchInstructions.add("jns");
		this.branchInstructions.add("je");
		this.branchInstructions.add("jz");
		this.branchInstructions.add("jne");
		this.branchInstructions.add("jnz");
		this.branchInstructions.add("jb");
		this.branchInstructions.add("jnae");
		this.branchInstructions.add("jc");
		this.branchInstructions.add("jnb");
		this.branchInstructions.add("jae");
		this.branchInstructions.add("jnc");
		this.branchInstructions.add("jbe");
		this.branchInstructions.add("jna");
		this.branchInstructions.add("ja");
		this.branchInstructions.add("jnbe");
		this.branchInstructions.add("jl");
		this.branchInstructions.add("jnge");
		this.branchInstructions.add("jge");
		this.branchInstructions.add("jnl");
		this.branchInstructions.add("jle");
		this.branchInstructions.add("jng");
		this.branchInstructions.add("jg");
		this.branchInstructions.add("jnle");
		this.branchInstructions.add("jp");
		this.branchInstructions.add("jpe");
		this.branchInstructions.add("jnp");
		this.branchInstructions.add("jpo");
		this.branchInstructions.add("jcxz");
		this.branchInstructions.add("jecxz");
		this.branchInstructions.add("jmp");
		
		this.callInstructions = new HashSet<String>();

	}
	
}
