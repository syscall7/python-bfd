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
public class ViewAssembly extends HTML implements ModelBinaryListener, ModelPlatformListener {
	
	private ModelBinary modelBinary;
	private ModelPlatform modelPlatform;
	StatusIndicator statusIndicator;
	
	private final DisassemblyServiceAsync disService = DisassemblyService.Util.getInstance();

	AsyncCallback<DisassemblyOutput> callback = new AsyncCallback<DisassemblyOutput>(){

	    @Override
	    public void onFailure(Throwable caught) {
	        //hexInput.hide();
	        //htmlDisplay.setHTML("Failed to get hex");
	    }

	    @Override
	    public void onSuccess(DisassemblyOutput result) {
	    	int PADDING = 150;
	    	setHTML(result.getFormattedAssembly());
	    	getParent().setHeight("" + (getOffsetHeight() + PADDING) + "px");
	    	statusIndicator.setBusy(false);
	    }};
	    
	
	public ViewAssembly(ModelBinary mb, ModelPlatform mp, StatusIndicator si)
	{
		modelBinary = mb;
		modelPlatform = mp;
		statusIndicator = si;
		
		modelBinary.addBinaryListner(this);
		modelPlatform.addPlatformListner(this);
	}
	
	public void onBinaryChange(ModelBinary mb)
	{
		setHTML("<br><center><i>Hit the Disassemble button to view the disassembly of the hex tab.</i></center>");
	}

	public void onPlatformChange(ModelPlatform mp)
	{
		statusIndicator.setBusy(true);
		setHTML("<H1>Loading</H1>");
		disService.disassemble(modelBinary.getBytes(), modelPlatform.getPlatform(), callback);
	}
	
	
}
