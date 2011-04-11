package com.reverbin.ODA.client;

import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.ClickEvent;

public class HexInput extends DialogBox  {
		
	public HexInput(final ModelBinary modelBinary) {
	//public HexInput(final ViewHex hexView) {
		super(true);
		setHTML("Hex Input");
		
		final FormPanel formPanel = new FormPanel();
		setWidget(formPanel);
		formPanel.setSize("100%", "100%");
		
		AbsolutePanel absolutePanel = new AbsolutePanel();
		formPanel.setWidget(absolutePanel);
		absolutePanel.setSize("300px", "185px");
		
		final TextArea txtrHex = new TextArea();
		absolutePanel.add(txtrHex, 0, 0);
		txtrHex.setSize("284px", "135px");
		
		Button btnSubmit = new Button("Submit");
		btnSubmit.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) 
			{	
				modelBinary.setBytes(HexUtils.textToBytes(txtrHex.getText()));
				hide();
				
			}
		});
		absolutePanel.add(btnSubmit, 10, 151);
	}

}
