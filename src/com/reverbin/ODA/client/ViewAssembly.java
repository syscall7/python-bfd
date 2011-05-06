package com.reverbin.ODA.client;

import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.*;
import com.reverbin.ODA.shared.DisassemblyOutput;
import com.google.gwt.event.dom.client.*;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;

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
	private final HTML html = new HTML();
	Button moreButton = new Button("Show More");
	private int currentOffset;
	private ViewPlatformSelection viewPlatform;
	
	private final DisassemblyServiceAsync disService = DisassemblyService.Util.getInstance();

	AsyncCallback<DisassemblyOutput> callback = new AsyncCallback<DisassemblyOutput>(){

	    @Override
	    public void onFailure(Throwable caught) {
	        //hexInput.hide();
	        //htmlDisplay.setHTML("Failed to get hex");
	    }

	    @Override
	    public void onSuccess(DisassemblyOutput result) {
	    	
	    	if (currentOffset == 0) {
	    		html.setHTML(result.getFormattedAssembly());
	    	} else {
	    		html.setHTML(html.getHTML() + result.getFormattedAssembly());
	    	}
	    	
	    	statusIndicator.setBusy(false);
	    	
	    	if ((result.getCurrentLines() + currentOffset) < result.getTotalLines()) {
	    		//moreButton.setVisible(true);
	    		add(moreButton);
	    		setCellHorizontalAlignment(moreButton, HasHorizontalAlignment.ALIGN_CENTER);
	    	}
	    	else {
	    		//moreButton.setVisible(false);
	    		remove(moreButton);
	    	}
	    	
	    	resize();
	    	
	    	currentOffset += result.getCurrentLines();

	    }};
	  
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
		
        this.add(viewPlatform);      
		this.add(html);
		this.add(moreButton);
		this.setCellHorizontalAlignment(moreButton, HasHorizontalAlignment.ALIGN_CENTER);
		this.setSpacing(10);
		this.setWidth("100%");
		moreButton.addClickHandler(this);
	}
	
	private void update()
	{
			currentOffset = 0;
			remove(moreButton);
			statusIndicator.setBusy(true);
			html.setHTML("<H1>Loading</H1>");
			
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
