package com.onlinedisassembler.server;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.math.BigInteger;

import com.onlinedisassembler.shared.DisassemblyOutput;
import com.onlinedisassembler.shared.PlatformDescriptor;
import com.onlinedisassembler.shared.PlatformId;



public class DisassemblyAnalyzer {

	private final int HEX_BYTE_DISPLAY_LEN = 8; 
	
	public DisassemblyAnalyzer() {
		this.instructionMap = new HashMap<Integer, Instruction>();
		this.stringList = new HashSet<String>();
		this.labels = new HashMap<Integer, String>();
		this.sections = new HashMap<Integer, CodeSection>();
		this.branches = new ArrayList<Branch>();
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
        output.setBranchTargetHtml(branchLineHtml.toString());
        return output;
	}
	
	public ArchAnalyzer archAnalyzerFactory( PlatformDescriptor platDesc )
	{
		if ( platDesc.platformId.equals(PlatformId.X86) )
		{
			return new x86Analyzer();
		}
		else if ( platDesc.platformId.equals(PlatformId.ARM) )
		{
			return new ArmAnalyzer();
		}
		else if ( platDesc.platformId.equals(PlatformId.MIPS) )
		{
			return new MipsAnalyzer();
		}
		else if ( platDesc.platformId.equals(PlatformId.PPC) )
		{
			return new PpcAnalyzer();
		}
		
		return null;
	}

	public String parseSectionData(String listing)
	{
		// ignore leading text
    	Pattern pattern = Pattern.compile("^\\s*[0-9]+\\s.*", Pattern.DOTALL | Pattern.MULTILINE);
        Matcher matcher = pattern.matcher(listing);
        matcher.find();
        listing = matcher.group();
     
        // now parse each line to get section data
        pattern = Pattern.compile(
                    // beginning of the line plus white space
                    "^\\s*" +               
                    // section index followed by white space
                    "([0-9]*)\\s+" +  
                    // Section name + white space
                    "([\\w\\.]+)\\s+" +
                    // Section size + white space
                    "([0-9a-f]+)\\s+" +
                    // VMA + white space
                    "([0-9a-f]+)\\s+" +
                    // LMA + white space
                    "([0-9a-f]+)\\s+" +
                    // File Offset + white space
                    "([0-9a-f]+)\\s+" +
                    // Alignment + white space
                    "2\\*\\*(\\d+)\\s+" +
                    // Flags
                    "(.*)$",
                    Pattern.MULTILINE);
        matcher = pattern.matcher(listing);
                
        // for each match (each line, really)
        while (matcher.find())
        {
        	CodeSection section = new CodeSection();
        	
        	section.index = Integer.parseInt(matcher.group(1), 16);
        	section.name = matcher.group(2);
        	section.size = Integer.parseInt(matcher.group(3), 16);
        	section.vma = Integer.parseInt(matcher.group(4), 16);
        	section.lma = Integer.parseInt(matcher.group(5), 16);
        	section.alignment = (int) Math.pow(2, Integer.parseInt(matcher.group(7))); 
        	section.flags = matcher.group(8);
        	
    		this.sections.put(section.index, section);

        }
                
        // Convert to HTML
    	ArrayList<Integer> sortedKeys=new ArrayList<Integer>(sections.keySet());
    	Collections.sort(sortedKeys);

    	// Create a formatted listing of instructions 
    	//	TODO: Determine initial buffer size better	    	
    	sectionHtml = new StringBuffer(sortedKeys.size()*20);	    	
    	
    	// Section Data should be displayed as a table
    	sectionHtml.append("<table id=\"sections\">");
    	
    	// Create the Table Header
    	sectionHtml.append("<tr>");
    	sectionHtml.append("<th>Index</th>");
    	sectionHtml.append("<th>Name</th>");
    	sectionHtml.append("<th>Size</th>");
    	sectionHtml.append("<th>Address</th>");
    	sectionHtml.append("<th>Align</th>");
    	sectionHtml.append("<th>Flags</th>");
    	sectionHtml.append("</tr>");
    	    	
    	// Parse the disassembly address by address
    	boolean alt = false;
    	for (int index : sortedKeys) {
    		CodeSection curSection = sections.get(index);
    		
    		// Handle alternating colors
    		if ( alt )
    		{
    			sectionHtml.append("<tr class=\"alt\">");	
    		}
    		else
    		{
    			sectionHtml.append("<tr>");	    			
    		}
    	
    		// Add Section Data
    		sectionHtml.append("<td>" + curSection.index  + "</td>");
    		
    		// Make a hyperlink for Loadable addresses
			if ( curSection.flags.contains("LOAD") )
			{
				sectionHtml.append(String.format("<td><a href=\"#disoff_%d\">%s</a></td>", curSection.vma, curSection.name));
			}
			else
			{
	    		sectionHtml.append("<td>" + curSection.name + "</td>");				
			}
			
    		sectionHtml.append("<td>" + String.format("0x%08x", curSection.size) + "\n</td>");
    		sectionHtml.append("<td>" + String.format("0x%08x", curSection.vma) + "\n</td>");
    		sectionHtml.append("<td>" + curSection.alignment  + "</td>");
    		sectionHtml.append("<td>" + curSection.flags + "</td>");
    
    		sectionHtml.append("</tr>");
    		alt = !alt;
    	}
        
    	sectionHtml.append("</table>");
    	    	
		return sectionHtml.toString();
	}
	
	public void parseObjdumpListing(String listing, int offset, int length, PlatformDescriptor platDesc)
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
		
        // Get an Instruction Analyzer
        ArchAnalyzer archAnalyzer = archAnalyzerFactory(platDesc);
        
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
        		int address = Integer.parseInt(matcher.group(1), 16);
        		
        		// Analyze the Instruction
        		Instruction instruction = archAnalyzer.analyzeInstruction(instr, address);
        		if ( instruction == null )
        		{
        			continue;
        		}
        		instruction.hexdata = matcher.group(2);
        		
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
        		
        		// Check if we need to create a label
        		if ( instruction.isTargetAddrValid )
        		{
        			// Check if a label exists for the target address
        			if ( !labels.containsKey(instruction.targetAddr) )
        			{
        				if ( instruction.instrType == InstructionType.BRANCH )
        				{
        					// Create a new label and add it to the labels map
        					String newLabel = "loc_" + Integer.toHexString(instruction.targetAddr);
        					labels.put(instruction.targetAddr, newLabel);
        					branches.add(new Branch(instruction));
        				}
        				else if ( instruction.instrType == InstructionType.CALL )
        				{
        					String newLabel = "func_" + Integer.toHexString(instruction.targetAddr);
        					labels.put(instruction.targetAddr, newLabel);
        				}
        			}
        			else
        			{
        				// Functions override branches
        				if ( instruction.instrType == InstructionType.CALL )
        				{
        					String newLabel = "func_" + Integer.toHexString(instruction.targetAddr);
        					labels.put(instruction.targetAddr, newLabel);
        				}        				
        			}
        		}
        		
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
    	
    	BranchLineHtmlFormatter blf = new BranchLineHtmlFormatter(this.branches);
    	
    	// Create a formatted listing of instructions 
    	//	TODO: Determine initial buffer size better
    	offsetHtml = new StringBuffer(sortedKeys.size()*20);	    	
    	rawBytesHtml = new StringBuffer(sortedKeys.size()*20);	    	
    	opcodeHtml = new StringBuffer(sortedKeys.size()*30);
    	branchLineHtml = new StringBuffer(sortedKeys.size()*30);
    	
    	// Parse the disassembly address by address
    	for (int address : sortedKeys) {
    		Instruction curInstr = instructionMap.get(address);
    		
    		String hexdata = curInstr.hexdata;
    		
    		// Check if this line needs a label
    		if ( labels.containsKey(address))
    		{
    			// Extra info for functions
    			if ( labels.get(address).startsWith("func") )
    			{
    				// Insert an extra line for functions
    				offsetHtml.append("<offset>" + String.format("0x%08x", address) +  "\n</offset>");
    				rawBytesHtml.append("<raw>\n</raw>");
    				opcodeHtml.append("<insn>; ------------ F U N C T I O N -------------\n</insn>");
    						
    			}
    			else
    			{
    	    		// Append branch line data for this address
    	    		blf.pushLabel();
    			}
    			
        		offsetHtml.append("<offset>" + String.format("0x%08x", address) +  "\n</offset>");
        		rawBytesHtml.append("<raw>\n</raw>");
        		
        		// Insert anchor for jumping to references.  Use ID for finding location of anchor in GWT
        		opcodeHtml.append("<insn>" + String.format("<a name=\"disoff_%d\" id=%d></a>", address, address) + labels.get(address) +  ":\n</insn>");
    		}
    		else
    		{
    			// Every address gets a link
    			opcodeHtml.append(String.format("<a name=\"disoff_%d\" id=%d></a>", address, address));
    		}
    		    		        		
    		// Only display first four bytes of hexdata 
    		// 	Add a "+" for lines with greater than 4 hex bytes
    		if ( hexdata.length() > HEX_BYTE_DISPLAY_LEN ) {
    			hexdata = hexdata.substring(0,HEX_BYTE_DISPLAY_LEN) + "+";
    		}
    		
    		// Format a single instruction
    		String instrText;
    		offsetHtml.append("<offset>" + String.format("0x%08x", address) +  "\n</offset>");
    		rawBytesHtml.append("<raw>" + hexdata +  "\n</raw>");
    		
			// Check if the instruction gets special handling
    		// Escape special characters in the opcode
    		String rawInstrText;
    		rawInstrText = curInstr.rawInstrStr.replaceAll("<", "&lt;");
    		rawInstrText = rawInstrText.replaceAll(">", "&gt;");

			if ( curInstr.instrType == InstructionType.BRANCH ||
				 curInstr.instrType == InstructionType.CALL	)
			{
				// Make sure the branch target actually exists
				if ( instructionMap.containsKey(curInstr.targetAddr) )
				{
					instrText = String.format("%-7s<a href=\"#disoff_%d\">%s</a>", curInstr.opcode, curInstr.targetAddr, labels.get(curInstr.targetAddr));	
					
				}
				else
				{
					// Branch target doesn't exist
					labels.remove(curInstr.targetAddr);
					instrText = String.format("%-7s <errinsn>0x%x</errinsn>", curInstr.opcode, curInstr.targetAddr);
				}
				
			}
			else
			{
				instrText = rawInstrText;
			}

    		
    		// Check for errors
    		if ( curInstr.isError )
    		{
    			instrText = String.format("<errinsn>     %s\n</errinsn>", instrText);
    		}
    		else
    		{
    			instrText = String.format("<insn>     %s\n</insn>", instrText);    			
    		}
    		
    		
    		// Append instruction
    		opcodeHtml.append(instrText);
    		
    		// Append branch line data for this address
    		blf.pushAddr(address);
    	}
    	
    	branchLineHtml.append(blf.finalizeHtml());

	}

	
	private int totalInstructionCount;
	private int currentInstructionCount;
    private HashSet<String> stringList;
	private HashMap<Integer, Instruction> instructionMap;
	private HashMap<Integer, String> labels;
	private HashMap<Integer, CodeSection> sections;
	private StringBuffer sectionHtml;
	private ArrayList<Branch> branches;
	private StringBuffer offsetHtml;
	private StringBuffer rawBytesHtml;
	private StringBuffer opcodeHtml;
	private StringBuffer branchLineHtml;
}
