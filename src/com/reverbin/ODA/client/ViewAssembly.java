package com.reverbin.ODA.client;

import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.*;
import com.reverbin.ODA.shared.DisassemblyOutput;
import com.reverbin.ODA.shared.Instruction;
import com.reverbin.ODA.shared.ObjectType;
import com.google.gwt.event.dom.client.*;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;

import java.awt.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;

/**
 * Container for assembly view
 * 
 * @author anthony
 *
 */
public class ViewAssembly extends VerticalPanel implements ModelPlatformBinListener, ClickHandler, SelectionHandler<Integer> {
	
	private final int HEX_BYTE_DISPLAY_LEN = 8; 
	private ModelPlatformBin modelPlatformBin;
	StatusIndicator statusIndicator;
	private final int CHUNK_LEN = 1000;
	private final VerticalPanel arrowpanel = new VerticalPanel();
	private final HTML opcodehtml = new HTML();
	private final HTML offsethtml = new HTML();
	private final HTML rawbyteshtml = new HTML();
	Button moreButton = new Button("Show More");
	private int currentOffset;
	VerticalPanel scrollContainer;
	HorizontalPanel disassemblyPanel;
	ScrollPanel scrollPanel;
	private ViewPlatformSelection viewPlatform;
	DialogObjectSupport dialogObjectSupport = new DialogObjectSupport();
	
	private final DisassemblyServiceAsync disService = DisassemblyService.Util.getInstance();

	AsyncCallback<DisassemblyOutput> callback = new AsyncCallback<DisassemblyOutput>(){

	    @Override
	    public void onFailure(Throwable caught) {
	        //hexInput.hide();
	        //htmlDisplay.setHTML("Failed to get hex");
	    }

	    @Override
	    public void onSuccess(DisassemblyOutput result) {
	    	
	    	convertDisToHtml(result);
	    	
	    	statusIndicator.setBusy(false);
	    	
	    	if ((result.getCurrentLines() + currentOffset) < result.getTotalLines()) {
	    		//moreButton.setVisible(true);
	    		scrollContainer.add(moreButton);
	    		scrollContainer.setCellHorizontalAlignment(moreButton, HasHorizontalAlignment.ALIGN_CENTER);
	    	}
	    	else {
	    		//moreButton.setVisible(false);
	    		scrollContainer.remove(moreButton);
	    	}
	    	
	    	//resize();
	    	
	    	currentOffset += result.getCurrentLines();
	    	
	    	if (result.getObjectType() != ObjectType.BINARY)
	    	{
	    		dialogObjectSupport.center();
	    		dialogObjectSupport.show();
	    	}

	    }};
	    
	    public void convertDisToHtml(DisassemblyOutput output)
	    {
	    	// Sort the Instructions by address
	    	ArrayList<Integer> sortedKeys=new ArrayList<Integer>(output.getInstructions().keySet());
	    	Collections.sort(sortedKeys);

	    	// Create a formatted listing of instructions 
	    	//	TODO: Determine initial buffer size better
	    	StringBuffer offsetBuf = new StringBuffer(sortedKeys.size()*20);	    	
	    	StringBuffer rawBytesBuf = new StringBuffer(sortedKeys.size()*20);	    	
	    	StringBuffer opcodeBuf = new StringBuffer(sortedKeys.size()*30);	    	

	    	HashMap<Integer,Instruction> instrMap = output.getInstructions();
	    	
	    	// Parse the disassembly address by address
	    	for (int address : sortedKeys) {
	    		Instruction curInstr = instrMap.get(address);
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
	    		offsetBuf.append("<offset>" + curInstr.addressFmt +  "\n</offset>");
	    		rawBytesBuf.append("<raw>" + hexdata +  "\n</raw>");
	    		if ( curInstr.isError )
	    		{	    			
	    			opcodeBuf.append("<errinsn>" + opcode +  "\n</errinsn>");
	    		}
	    		else
	    		{
	    			opcodeBuf.append("<insn>" + opcode +  "\n</insn>");
	    		}
	    	}

	    	// Populate panels with disassembly while accounting
	    	//	for existing disassembly
	    	if (currentOffset == 0) {
	    		opcodehtml.setHTML(opcodeBuf.toString());
	    		rawbyteshtml.setHTML(rawBytesBuf.toString());
	    		offsethtml.setHTML(offsetBuf.toString());
	    	} else {
	    		opcodehtml.setHTML(opcodehtml.getHTML() + opcodeBuf.toString());	    		
	    		rawbyteshtml.setHTML(rawbyteshtml.getHTML() + rawBytesBuf.toString());	    		
	    		offsethtml.setHTML(offsethtml.getHTML() + offsetBuf.toString());	    			    	
	    	}
	    }
	  
	private void resize()
	{
    	int PADDING = 0;
		getParent().setHeight((getOffsetHeight()+PADDING)+"px");
	}
	
	public ViewAssembly(ModelPlatformBin mpb, StatusIndicator si)
	{
		modelPlatformBin = mpb;
		statusIndicator = si;
		currentOffset = 0;
		
		modelPlatformBin.addListener(this);
		viewPlatform = new ViewPlatformSelection(modelPlatformBin);
		disassemblyPanel = new HorizontalPanel();
		scrollPanel = new ScrollPanel();
		scrollContainer = new VerticalPanel();
		
		//disassemblyPanel.setWidth("100%");
		//scrollContainer.setWidth("100%");
		scrollContainer.add(disassemblyPanel);
		scrollContainer.add(moreButton);
		scrollPanel.add(scrollContainer);
        //scrollPanel.setWidth("100%");
        scrollPanel.setHeight("418px");
        //scrollPanel.setAlwaysShowScrollBars(true);
		this.add(viewPlatform);
		
		// The disassembly view is divided up into
		//	separate panels for the offset, raw bytes
		//	and the opcode. A panel for adding arrows in
		//	the future is also included
		arrowpanel.setWidth("25px");
        offsethtml.setWidth("95px");
        rawbyteshtml.setWidth("80px");
        opcodehtml.setWidth("390px");
        disassemblyPanel.add(arrowpanel);
        disassemblyPanel.add(offsethtml);
        disassemblyPanel.add(rawbyteshtml);
        disassemblyPanel.add(opcodehtml);

		this.add(scrollPanel);
		scrollContainer.setCellHorizontalAlignment(moreButton, HasHorizontalAlignment.ALIGN_CENTER);
		this.setSpacing(10);
		//this.setWidth("100%");
		moreButton.addClickHandler(this);
	}
	
	private void update()
	{
			currentOffset = 0;
			scrollContainer.remove(moreButton);
			statusIndicator.setBusy(true);
			
			// Display "Loading" and remove the rest of the code
			opcodehtml.setHTML("<H1><left>Loading</left></H1>");
			offsethtml.setHTML("");
			rawbyteshtml.setHTML("");
			
			disService.disassemble(modelPlatformBin.getBytes(), modelPlatformBin.getPlatform(), currentOffset, CHUNK_LEN, callback);
	}
	
	public void onChange(ModelPlatformBin mpb, int eventFlags)
	{
		update();
	}

	@Override
	public void onClick(ClickEvent event) {
		disService.disassemble(modelPlatformBin.getBytes(), modelPlatformBin.getPlatform(), currentOffset, CHUNK_LEN, callback);
	}
	
	@Override
	public void onSelection(SelectionEvent<Integer> event) {
		//TODO: get rid of hard-coded value here
		if (event.getSelectedItem() == 1)
			resize();		
	}
	
}
