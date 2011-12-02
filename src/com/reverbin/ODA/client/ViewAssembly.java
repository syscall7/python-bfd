package com.reverbin.ODA.client;

import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.*;
import com.reverbin.ODA.server.Instruction;
import com.reverbin.ODA.shared.DisassemblyOutput;
import com.reverbin.ODA.shared.ObjectType;
import com.google.gwt.event.dom.client.*;
import com.google.gwt.event.logical.shared.ResizeEvent;
import com.google.gwt.event.logical.shared.ResizeHandler;
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
	
	private ModelPlatformBin modelPlatformBin;
	StatusIndicator statusIndicator;
	private final int CHUNK_LEN = 1000;
	private final HTML branchTargetLines = new HTML();
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
	public HashMap<Integer, Integer> addrToLineMap;
	
	private final DisassemblyServiceAsync disService = DisassemblyService.Util.getInstance();

	AsyncCallback<DisassemblyOutput> callback = new AsyncCallback<DisassemblyOutput>(){

	    @Override
	    public void onFailure(Throwable caught) {
	        //hexInput.hide();
	        //htmlDisplay.setHTML("Failed to get hex");
	    }

	    @Override
	    public void onSuccess(DisassemblyOutput result) {
	    	
	    	// Populate panels with disassembly while accounting
	    	//	for existing disassembly
	    	if (currentOffset == 0) {
	    		opcodehtml.setHTML(result.getOpcodeHtml());
	    		rawbyteshtml.setHTML(result.getRawBytesHtml());
	    		offsethtml.setHTML(result.getOffsetHtml());
	    		branchTargetLines.setHTML(result.getBranchTargetHtml());
	    	} else {
	    		opcodehtml.setHTML(opcodehtml.getHTML() + result.getOpcodeHtml());	    		
	    		rawbyteshtml.setHTML(rawbyteshtml.getHTML() + result.getRawBytesHtml());	    		
	    		offsethtml.setHTML(offsethtml.getHTML() + result.getOffsetHtml());	   
	    		branchTargetLines.setHTML(branchTargetLines.getHTML() + result.getBranchTargetHtml());
	    	}	    	
	    	
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
	    	
	    	// Save the Address Map
	    	addrToLineMap = result.getAddrToLineMap();

	    }};
	    
	  
	private void resize()
	{
    	int remainingSpace = Window.getClientHeight() - scrollPanel.getAbsoluteTop();
    	if ( remainingSpace < Main.MIN_DIS_DISPLAY_SIZE )
    	{
        	scrollPanel.setHeight( Main.MIN_DIS_DISPLAY_SIZE - Main.MIN_DIS_DISPLAY_MARGIN + "px");    		
    	}
    	else
    	{
    		scrollPanel.setHeight( remainingSpace - Main.MIN_DIS_DISPLAY_MARGIN + "px");
    	}
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
		
		scrollContainer.add(disassemblyPanel);
		scrollContainer.add(moreButton);
		scrollPanel.add(scrollContainer);
		this.add(viewPlatform);
		
		
		// The disassembly view is divided up into
		//	separate panels for the offset, raw bytes
		//	and the opcode. A panel for adding arrows in
		//	the future is also included
		//branchTargetLines.setWidth("25px");
        offsethtml.setWidth("95px");
        rawbyteshtml.setWidth("80px");
        opcodehtml.setWidth("390px");
        disassemblyPanel.add(branchTargetLines);
        disassemblyPanel.add(offsethtml);
        disassemblyPanel.add(rawbyteshtml);
        disassemblyPanel.add(opcodehtml);

		this.add(scrollPanel);
		scrollContainer.setCellHorizontalAlignment(moreButton, HasHorizontalAlignment.ALIGN_CENTER);
		this.setSpacing(10);
		//this.setWidth("100%");
		moreButton.addClickHandler(this);
		resize();
		
		Window.addResizeHandler(new ResizeHandler() {
       	 public void onResize(ResizeEvent event) {
       		 resize();
       	 }
        });
		
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
