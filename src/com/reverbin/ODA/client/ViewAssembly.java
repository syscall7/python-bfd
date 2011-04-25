package com.reverbin.ODA.client;

import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.*;
import com.reverbin.ODA.shared.DisassemblyOutput;
import com.reverbin.ODA.shared.PlatformDescriptor;
import com.google.gwt.event.dom.client.*;

/**
 * Container for assembly view
 * 
 * @author anthony
 *
 */
public class ViewAssembly extends VerticalPanel implements ModelBinaryListener, ModelPlatformListener, ClickHandler {
	
	private ModelBinary modelBinary;
	private ModelPlatform modelPlatform;
	StatusIndicator statusIndicator;
	private final int CHUNK_LEN = 1000;
	private final HTML html = new HTML();
	Button moreButton = new Button("Show More");
	private int currentOffset;
	private ViewPlatformSelection viewPlatform;
	private boolean inProgress = false;
	
	private final DisassemblyServiceAsync disService = DisassemblyService.Util.getInstance();

	AsyncCallback<DisassemblyOutput> callback = new AsyncCallback<DisassemblyOutput>(){

	    @Override
	    public void onFailure(Throwable caught) {
	        //hexInput.hide();
	        //htmlDisplay.setHTML("Failed to get hex");
	    }

	    @Override
	    public void onSuccess(DisassemblyOutput result) {
	    	int PADDING = 0;
	    	
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
	    	
	    	getParent().setHeight((getOffsetHeight()+PADDING)+"px");
	    	
	    	currentOffset += result.getCurrentLines();
	    	
	    	inProgress = false;
	    }};
	    
	
	public ViewAssembly(ModelBinary mb, ModelPlatform mp, StatusIndicator si)
	{
		modelBinary = mb;
		modelPlatform = mp;
		statusIndicator = si;
		currentOffset = 0;
		
		modelBinary.addBinaryListner(this);
		modelPlatform.addPlatformListner(this);
		viewPlatform = new ViewPlatformSelection(modelPlatform);
		
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
		if (!inProgress)
		{
			currentOffset = 0;
			remove(moreButton);
			statusIndicator.setBusy(true);
			html.setHTML("<H1>Loading</H1>");
			
			inProgress = true;
			disService.disassemble(modelBinary.getBytes(), modelPlatform.getPlatform(), currentOffset, CHUNK_LEN, callback);
		}
	}
	
	public void onBinaryChange(ModelBinary mb)
	{
		update();
	}

	public void onPlatformChange(ModelPlatform mp)
	{
		update();
	}

	@Override
	public void onClick(ClickEvent event) {
		inProgress = true;
		disService.disassemble(modelBinary.getBytes(), modelPlatform.getPlatform(), currentOffset, CHUNK_LEN, callback);
	}
	
	
}
