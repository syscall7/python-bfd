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

public class DialogHelp extends DialogBox {

	private final Button buttonOk = new Button("Ok");
	private final HTML body = new HTML();
	
	public DialogHelp()
	{
		LayoutPanel lp = new LayoutPanel();
		lp.setSize("350px", "400px");
		ScrollPanel scrollPanel = new ScrollPanel();
		scrollPanel.setStyleName("borderedPanel");
		VerticalPanel panel = new VerticalPanel();
		panel.setSpacing(10);
		String help = Resources.INSTANCE.help().getText();
		setHTML("Help");
		
		// Add a click handler to the Ok button
		buttonOk.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				hide();
			}
		});
		
		body.setHTML(help);
		scrollPanel.add(body);
		lp.add(scrollPanel);
		panel.add(lp);
		panel.add(buttonOk);
		panel.setCellWidth(buttonOk, "100%");
		panel.setCellHorizontalAlignment(buttonOk, HasHorizontalAlignment.ALIGN_CENTER);
		add(panel);
		//this.setSize( , height)
		
	}
}
