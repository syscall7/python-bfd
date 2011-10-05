package com.reverbin.ODA.client;


import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.LayoutPanel;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.VerticalPanel;

public class DialogObjectSupport extends DialogBox {

	private final Button buttonOk = new Button("Ok");
	private final HTML body = new HTML();
	
	public DialogObjectSupport()
	{
		VerticalPanel panel = new VerticalPanel();
		panel.setSpacing(10);
		String help = Resources.INSTANCE.objectSupport().getText();
		setHTML("Coming Soon!");
		
		// Add a click handler to the Ok button
		buttonOk.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				hide();
			}
		});
		
		body.setHTML(help);
		//scrollPanel.add(body);
		//lp.add(scrollPanel);
		panel.add(body);
		panel.add(buttonOk);
		panel.setCellWidth(buttonOk, "100%");
		panel.setCellHorizontalAlignment(buttonOk, HasHorizontalAlignment.ALIGN_CENTER);
		add(panel);
		//this.setSize( , height)
		
	}
}
