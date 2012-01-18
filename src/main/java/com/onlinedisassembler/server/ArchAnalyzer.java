package com.onlinedisassembler.server;

import java.util.HashSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


public abstract class ArchAnalyzer {
	
	public Instruction analyzeInstruction(String instructionStr, int address) {
		
		Instruction instruction = new Instruction();
		
		if ( instructionStr == null )
		{
			return null;
		}
		
		// TODO: Strip out comments
		
		instruction.address = address;
		instruction.rawInstrStr = instructionStr;
		
		// Separate out the opcode
		opcodeMatcher = opcodePattern.matcher(instructionStr);
		if ( !opcodeMatcher.find() )
		{
			instruction.isError = true;
			instruction.errorType = "INVALID";
			return instruction;
		}
		instruction.opcode = opcodeMatcher.group(1).trim();
		
		// Separate out the registers
		if ( opcodeMatcher.group(3) != null )
		{
			instruction.registers = opcodeMatcher.group(3).trim();
		}
		
		// Determine the type of instruction 
		instruction.instrType = getInstructionType(instruction.opcode);
		if ( instruction.instrType == InstructionType.BRANCH ||
			 instruction.instrType == InstructionType.CALL	)
		{
			computeTargetAddress(instruction);
		}
		
		
		return instruction;
	}
	
	protected InstructionType getInstructionType(String opcode)
	{
		// TODO: Flesh the rest of this out
		if ( branchInstructions.contains(opcode) )
		{
			return InstructionType.BRANCH;
		}
		else if ( callInstructions.contains(opcode) )
		{
			return InstructionType.CALL;
		}
		
		return InstructionType.NOP;
	}

	protected void computeTargetAddress(Instruction instruction)
	{
		// Simple targets
		if ( branchInstructions.contains(instruction.opcode) ||
			 callInstructions.contains(instruction.opcode) )
		{
			instruction.isTargetAddrValid = true;
			try
			{
				String addr = instruction.registers.split("\\s")[0];
				if (!addr.startsWith("0x"))
					addr = "0x" + addr;
				instruction.targetAddr = Long.decode(addr).intValue();
			}
			catch (NumberFormatException e)
			{
				instruction.isTargetAddrValid = false;
			}
			catch (Exception e)
			{
				instruction.isTargetAddrValid = false;
			}
		}
		
		return;
	}
	
	protected HashSet<String> branchInstructions;
	protected HashSet<String> callInstructions;
    protected Pattern opcodePattern;
    protected Matcher opcodeMatcher;
}
