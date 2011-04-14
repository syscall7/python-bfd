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
	BusyAnimation busyAnimation;
	
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
	    	busyAnimation.cancel();
	    }};
	    
	
	public ViewAssembly(ModelBinary mb, ModelPlatform mp, BusyAnimation ba)
	{
		modelBinary = mb;
		modelPlatform = mp;
		busyAnimation = ba;
		
		modelBinary.addBinaryListner(this);
		modelPlatform.addPlatformListner(this);
	}
	
	public void onBinaryChange(ModelBinary mb)
	{
		setHTML("");
	}

	public void onPlatformChange(ModelPlatform mp)
	{
		busyAnimation.run(Integer.MAX_VALUE);
		disService.disassemble(modelBinary.getBytes(), modelPlatform.getPlatform(), callback);
	}
	
	
}
