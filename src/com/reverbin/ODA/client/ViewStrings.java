package com.reverbin.ODA.client;

import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;

public class ViewStrings extends FlowPanel implements ModelBinaryListener, SelectionHandler<Integer> {
	
	private ModelBinary modelBinary;
	StatusIndicator statusIndicator;
	HTML html = new HTML();
	
	private final DisassemblyServiceAsync disService = DisassemblyService.Util.getInstance();

	AsyncCallback<String> callback = new AsyncCallback<String>(){

	    @Override
	    public void onFailure(Throwable caught) {
	        //hexInput.hide();
	        //htmlDisplay.setHTML("Failed to get hex");
	    }

	    @Override
	    public void onSuccess(String result) {

	    	html.setHTML(result);
	    	update();
	    	statusIndicator.setBusy(false);
	    }};
	
	private void update()
	{
    	int PADDING = 10;
    	setHeight("" + (html.getOffsetHeight() + PADDING) + "px");
	}
	
	public ViewStrings(ModelBinary mb, StatusIndicator si)
	{
		modelBinary = mb;
		statusIndicator = si;
		
		modelBinary.addBinaryListner(this);
		add(html);
	}
	
	public void onBinaryChange(ModelBinary mb)
	{
		html.setHTML("<H1><center>Loading Strings</center></H1>");
		disService.strings(modelBinary.getBytes(), callback);
	}
	@Override
	public void onSelection(SelectionEvent<Integer> event) {
		//TODO: get rid of hard-coded value here
		if (event.getSelectedItem() == 2)
			update();		
	}
}
