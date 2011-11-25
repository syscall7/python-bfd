package com.reverbin.ODA.server;

import java.util.HashSet;
import java.util.regex.Pattern;


public class ArmAnalyzer extends ArchAnalyzer {
	
	public ArmAnalyzer(){
		
		// Initialize the opcode pattern for this architecture
		//	Note: arm opcodes can have a period in them
		opcodePattern = Pattern.compile("([\\w\\.]+)(\\s+(.+))?");
		
		// Add all of the branch instructions
		this.branchInstructions = new HashSet<String>();
		this.branchInstructions.add("bne");
		this.branchInstructions.add("beq");
		this.branchInstructions.add("bcs");
		this.branchInstructions.add("bcc");
		this.branchInstructions.add("bmi");
		this.branchInstructions.add("bpl");
		this.branchInstructions.add("bvs");
		this.branchInstructions.add("bvc");
		this.branchInstructions.add("bhi");
		this.branchInstructions.add("bls");
		this.branchInstructions.add("bge");
		this.branchInstructions.add("blt");
		this.branchInstructions.add("bgt");
		this.branchInstructions.add("ble");
		this.branchInstructions.add("b");

		// Add Thumb branches instructions
		this.branchInstructions.add("bne.n");
		this.branchInstructions.add("beq.n");
		this.branchInstructions.add("bcs.n");
		this.branchInstructions.add("bcc.n");
		this.branchInstructions.add("bmi.n");
		this.branchInstructions.add("bpl.n");
		this.branchInstructions.add("bvs.n");
		this.branchInstructions.add("bvc.n");
		this.branchInstructions.add("bhi.n");
		this.branchInstructions.add("bls.n");
		this.branchInstructions.add("bge.n");
		this.branchInstructions.add("blt.n");
		this.branchInstructions.add("bgt.n");
		this.branchInstructions.add("ble.n");
		this.branchInstructions.add("b.n");
		
		this.callInstructions = new HashSet<String>();
		this.callInstructions.add("bl");
	}
	
	
}
