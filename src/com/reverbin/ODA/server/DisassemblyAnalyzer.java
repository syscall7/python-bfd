package com.reverbin.ODA.server;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.reverbin.ODA.shared.Instruction;
import com.reverbin.ODA.shared.DisassemblyOutput;

public class DisassemblyAnalyzer {

	private final int HEX_BYTE_DISPLAY_LEN = 8; 
	
	public DisassemblyAnalyzer() {
		this.instructionMap = new HashMap<Integer, Instruction>();
		this.stringList = new HashSet<String>();
	}
	
	public HashMap<Integer, Instruction> getInstructions() {
		return this.instructionMap;
	}
	
	
	public void addString(String string){
		stringList.add(string);
	}
	
	public HashSet<String> getStrings()
	{
		return stringList;
	}
	
	public DisassemblyOutput getDisassemblyOutput()
	{
		DisassemblyOutput output = new DisassemblyOutput();
		
        output.setTotalLines(totalInstructionCount);
        output.setCurrentLines(currentInstructionCount);
        output.setOffsetHtml(offsetHtml.toString());
        output.setOpcodeHtml(opcodeHtml.toString());
        output.setRawBytesHtml(rawBytesHtml.toString());
        
        return output;
	}
	
	public void parseObjdumpListing(String listing, int offset, int length)
	{
    	// ignore leading text
    	Pattern pattern = Pattern.compile("^\\s*[0-9a-fA-F]+:.*", Pattern.DOTALL | Pattern.MULTILINE);
        Matcher matcher = pattern.matcher(listing);
        matcher.find();
        listing = matcher.group();
        //final int MAX_LINES = 2000;
        int line = 0;
        currentInstructionCount = 0;
        totalInstructionCount = 0;		
		
        // Create pattern to identify and save errors in the disassembly
        //	ARM = <errortype>
        //	x86 - (bad)
        Pattern errorInstPattern = Pattern.compile("(<.+>|" + Pattern.quote("(bad)") + ")");
        Matcher errorInstMatcher;
        
        // now parse each line to get the offset, raw bytes and instruction
        pattern = Pattern.compile(
                    // beginning of the line plus white space
                    "^\\s*" +               
                    // offset and colon followed by white space
                    "([0-9a-f]*):\\s+" +    
                    // raw binary bytes "xxxxxxxx" or "xx xx xx .."
                    "([0-9a-f]{8}|(?:[0-9a-f]{2} )+|(?:[0-9a-f]{4} )+)" +
                    // instruction
                    "(.*)$",
                    Pattern.MULTILINE);
        matcher = pattern.matcher(listing);
                
        // for each match (each line, really)
        while (matcher.find())
        {       	
        		
        	totalInstructionCount++;
        	
        	if (line++ < offset) {
        		continue;
        	}
        	
        	if (currentInstructionCount < length)
        	{
        		String instr = matcher.group(3).trim();
        		Instruction instruction = new Instruction();
        		
        		// Save Instruction Data
        		//	TODO: Save registers separately
        		instruction.address = Integer.parseInt(matcher.group(1), 16);
        		instruction.hexdata = matcher.group(2);
        		instruction.opcode = instr;
        		instruction.addressFmt = String.format("0x%08x", instruction.address);
        		
        		// Look for errors in the opcode
        		errorInstMatcher = errorInstPattern.matcher(instr);
        		if ( errorInstMatcher.find() )
        		{
        			instruction.isError = true;
        			instruction.errorType = errorInstMatcher.group(1);
        		}
        		
        		// Format hex data the same for all processors
        		//	(objdump doesn't do it)
        		instruction.hexdata = instruction.hexdata.replace(" ", ""); 
        		
        		// Store the meta data
        		instructionMap.put(instruction.address, instruction);
        			            
	        	currentInstructionCount++;
        	}	        	
        }
        
        convertToHtml();

	}
	
	private void convertToHtml()
	{
    	// Sort the Instructions by address
    	ArrayList<Integer> sortedKeys=new ArrayList<Integer>(instructionMap.keySet());
    	Collections.sort(sortedKeys);

    	// Create a formatted listing of instructions 
    	//	TODO: Determine initial buffer size better
    	offsetHtml = new StringBuffer(sortedKeys.size()*20);	    	
    	rawBytesHtml = new StringBuffer(sortedKeys.size()*20);	    	
    	opcodeHtml = new StringBuffer(sortedKeys.size()*30);	    	
    	
    	// Parse the disassembly address by address
    	for (int address : sortedKeys) {
    		Instruction curInstr = instructionMap.get(address);
    		String opcode = curInstr.opcode;
    		String hexdata = curInstr.hexdata;
    		
    		// Escape special characters in the opcode
    		opcode = opcode.replaceAll("<", "&lt;");
    		opcode = opcode.replaceAll(">", "&gt;");
    		        		
    		// Only display first four bytes of hexdata 
    		// 	Add a "+" for lines with greater than 4 hex bytes
    		if ( hexdata.length() > HEX_BYTE_DISPLAY_LEN ) {
    			hexdata = hexdata.substring(0,HEX_BYTE_DISPLAY_LEN) + "+";
    		}
    		
    		// Format a single instruction
    		offsetHtml.append("<offset>" + curInstr.addressFmt +  "\n</offset>");
    		rawBytesHtml.append("<raw>" + hexdata +  "\n</raw>");
    		if ( curInstr.isError )
    		{	    			
    			opcodeHtml.append("<errinsn>" + opcode +  "\n</errinsn>");
    		}
    		else
    		{
    			opcodeHtml.append("<insn>" + opcode +  "\n</insn>");
    		}
    	}

	}

	private int totalInstructionCount;
	private int currentInstructionCount;
    private HashSet<String> stringList;
	private HashMap<Integer, Instruction> instructionMap;
	private StringBuffer offsetHtml;
	private StringBuffer rawBytesHtml;
	private StringBuffer opcodeHtml;
}
