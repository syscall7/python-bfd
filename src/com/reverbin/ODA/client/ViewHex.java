/**
 * 
 */
package com.reverbin.ODA.client;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.*;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;

/**
 * Container for hex view
 * 
 * @author anthony
 *
 */
public class ViewHex extends FlowPanel implements ModelBinaryListener, ClickHandler, SubmitCompleteHandler {

	private ModelBinary modelBinary;
	private TextArea textArea = new TextArea();
	Button hexEditButton = new Button("Edit");
	Button hexUploadButton = new Button("Upload File");
	UploadFile uploadFile = new UploadFile(this);
	
	/**
	 * Constructor
	 * @param asmView
	 */
	public ViewHex(ModelBinary mb) {
		modelBinary = mb;
		mb.addBinaryListner(this);
		textArea.setReadOnly(true);
	}
	
	protected void onLoad()
	{
		hexEditButton.addClickHandler(this);
		hexUploadButton.addClickHandler(this);
		
        FlowPanel hexHeaderPanel = new FlowPanel();
        HorizontalPanel firstRow = new HorizontalPanel();   
        firstRow.add(hexUploadButton);
        firstRow.add(hexEditButton);
        hexHeaderPanel.add(firstRow);
        hexHeaderPanel.setStyleName("panelBox");
        int clientHeight = Window.getClientHeight();
        textArea.setSize("574px", "" + (int) (clientHeight*2/3) + "px");
        textArea.setStyleName("textarea");

        this.add(hexHeaderPanel);
        this.add(textArea);
        this.setSize("600px", "" + (int) (clientHeight*2/3 + 82) + "px" );
	}

	@Override
	public void onBinaryChange(ModelBinary mb) {
		textArea.setText(HexUtils.bytesToText(modelBinary.getBytes()));
	}

	@Override
	public void onClick(ClickEvent event) {
		
		if (event.getSource().equals(hexEditButton)) {
			if (textArea.isReadOnly()) {
				textArea.setReadOnly(false);
				hexEditButton.setText("Save");
				textArea.setFocus(true);
				textArea.setCursorPos(0);
			}
			else {
				modelBinary.setBytes(HexUtils.textToBytes(textArea.getText()));
				textArea.setReadOnly(true);
				hexEditButton.setText("Edit");
			}
		} else {

       	 	uploadFile.center();
       	 	uploadFile.show();
		}
	}

	@Override
	public void onSubmitComplete(SubmitCompleteEvent event) {
		modelBinary.setBytes(HexUtils.textToBytes(event.getResults()));
		uploadFile.hide();
	}
}
