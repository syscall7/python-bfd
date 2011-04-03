package com.reverbin.ODA.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitEvent;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;

public class UploadFile extends DialogBox {
	
	private static final String UPLOAD_ACTION_URL = GWT.getModuleBaseURL() + "upload";
	private final Button buttonSubmit = new Button("Submit");
	
	public UploadFile() {
		setHTML("Upload File");
		
        // Create a FormPanel and point it at a service.
		final FormPanel uploadForm = new FormPanel();
		uploadForm.setAction(UPLOAD_ACTION_URL);
		 
		// Because we're going to add a FileUpload widget, we'll need to set the
		// form to use the POST method, and multipart MIME encoding.
		uploadForm.setEncoding(FormPanel.ENCODING_MULTIPART);
		uploadForm.setMethod(FormPanel.METHOD_POST);
		
		// Create a panel to hold all of the form widgets.
		VerticalPanel panel = new VerticalPanel();
		uploadForm.setWidget(panel);
		
		// Create a FileUpload widget.
		FileUpload fileUpload = new FileUpload();
		fileUpload.setName("uploadFormElement");
		panel.add(fileUpload);
		
		// Add a click handler to the submit button
		buttonSubmit.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				UploadFile.this.buttonSubmit.setEnabled(false);
				uploadForm.submit();
			}
		});
		
		panel.add(buttonSubmit);
		
		// Add an event handler to the form.
		uploadForm.addSubmitHandler(new FormPanel.SubmitHandler() {
			@Override
			public void onSubmit(SubmitEvent event) {
				// This event is fired just before the form is submitted. We can
				// take this opportunity to perform validation.
			}
		});

	    uploadForm.addSubmitCompleteHandler(new FormPanel.SubmitCompleteHandler() {
			@Override
			public void onSubmitComplete(SubmitCompleteEvent event) {
				// Check results here
				
				UploadFile.this.hide();
				
			}
		});

		this.add(uploadForm);
	}

}
