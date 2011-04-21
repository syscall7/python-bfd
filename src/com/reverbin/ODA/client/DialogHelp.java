package com.reverbin.ODA.client;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.VerticalPanel;

public class DialogHelp extends DialogBox {

	private final Button buttonOk = new Button("Ok");
	private final HTML body = new HTML();
	
	public DialogHelp()
	{
		VerticalPanel panel = new VerticalPanel();
		setHTML("About ODA");
		
		// Add a click handler to the submit button
		buttonOk.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				hide();
			}
		});
		
		body.setHTML("This is some text");
		panel.add(body);
		panel.add(buttonOk);
		panel.setCellWidth(buttonOk, "100%");
		panel.setCellHorizontalAlignment(buttonOk, HasHorizontalAlignment.ALIGN_RIGHT);
		add(panel);
		
	}
}
