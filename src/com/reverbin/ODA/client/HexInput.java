package com.reverbin.ODA.client;

import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.reverbin.ODA.shared.FormattedOutput;

public class HexInput extends DialogBox  {
		
	public HexInput(final ViewUpdater viewUpdater) {
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
			public void onClick(ClickEvent event) {	
				char[] hex = txtrHex.getText().replaceAll(" ", "").toCharArray();
				int length = hex.length / 2;
			    byte[] raw = new byte[length];
			    for (int i = 0; i < length; i++) {
			      int high = Character.digit(hex[i * 2], 16);
			      int low = Character.digit(hex[i * 2 + 1], 16);
			      int value = (high << 4) | low;
			      if (value > 127)
			        value -= 256;
			      raw[i] = (byte) value;
			    }
				
			    viewUpdater.updateHex(raw);		    
			}
		});
		absolutePanel.add(btnSubmit, 10, 151);
	}

}
