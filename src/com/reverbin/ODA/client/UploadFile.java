package com.reverbin.ODA.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.CheckBox;

public class UploadFile extends DialogBox {
	
	private static final String UPLOAD_ACTION_URL = GWT.getModuleBaseURL() + "upload";
	private final Button buttonSubmit = new Button("Submit");
	private final Button buttonCancel = new Button("Cancel");
	private final CheckBox legalCheckbox = new CheckBox("I Agree");
	
	public UploadFile(SubmitCompleteHandler submitCompleteHandler) {
		
		setHTML("<center>Upload File</center>");
		Image img = new Image("images/upload.png");
		
        // Create a FormPanel and point it at a service.
		final FormPanel uploadForm = new FormPanel();
		uploadForm.setAction(UPLOAD_ACTION_URL);
		 
		// Because we're going to add a FileUpload widget, we'll need to set the
		// form to use the POST method, and multipart MIME encoding.
		uploadForm.setEncoding(FormPanel.ENCODING_MULTIPART);
		uploadForm.setMethod(FormPanel.METHOD_POST);
		
		// Create a panel to hold all of the form widgets.
		VerticalPanel panel = new VerticalPanel();
		panel.setSpacing(5);
		uploadForm.setWidget(panel);
		
		// Create a FileUpload widget.
		final FileUpload fileUpload = new FileUpload();
		fileUpload.setName("uploadFormElement");

		// Submit button is disabled when the box first appears
		buttonSubmit.setEnabled(false);
		
		// Create text for legal disclaimers
		ScrollPanel scrollPanel = new ScrollPanel();
		scrollPanel.setStyleName("borderedPanel");
		String legalText = Resources.INSTANCE.legalAgreement().getText();
		setHTML("File Upload");
		HTML body = new HTML();
		body.setHTML(legalText);
		body.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
		scrollPanel.add(body);
		scrollPanel.setHeight("100px");
		
		// Legalese Panel is a composite panel containing a
		//	labels, other panels and a checkbox
		VerticalPanel legalesePanel = new VerticalPanel();
		legalesePanel.setWidth("100%");
		legalesePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		legalesePanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		legalesePanel.setTitle("LegalAgreement");
		legalesePanel.add(scrollPanel);

		// Add an agreement checkbox
		HorizontalPanel agreementPanel = new HorizontalPanel();
		agreementPanel.add(legalCheckbox);
		legalesePanel.add(agreementPanel);
	    
		// Add the upload widgets
		HorizontalPanel topRow = new HorizontalPanel();
		topRow.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		topRow.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		topRow.setWidth("100%");
		topRow.add(img);
		topRow.add(fileUpload);
		topRow.setCellHorizontalAlignment(img, HasHorizontalAlignment.ALIGN_RIGHT);
		topRow.setCellHorizontalAlignment(fileUpload, HasHorizontalAlignment.ALIGN_RIGHT);
		panel.add(topRow);
		panel.add(legalesePanel);
		
		// Add a click handler to the submit button
		buttonSubmit.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				//UploadFile.this.buttonSubmit.setEnabled(false);
				uploadForm.submit();
			}
		});

		// Add a click handler to the agreement checkbox
		//	that enables/disables the submit button
		legalCheckbox.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				buttonSubmit.setEnabled(!buttonSubmit.isEnabled());
			}
		});		
		
		// Add a click handler to the cancel button
		buttonCancel.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				//UploadFile.this.buttonSubmit.setEnabled(false);
				hide();
			}
		});
		
	    // Add an event handler to the form.
	    uploadForm.addSubmitHandler(new FormPanel.SubmitHandler() {
	      public void onSubmit(SubmitEvent event) {
	        // This event is fired just before the form is submitted. We can take
	        // this opportunity to perform validation.
	    	
	        if (fileUpload.getFilename().length() == 0) {
	          Window.alert("Please select a file to upload.");
	          event.cancel();
	        }
	      }
	    });

		
		// Add submit and cancel buttons
		HorizontalPanel hp = new HorizontalPanel();
		hp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		hp.setWidth("100%");
		hp.add(buttonSubmit);
		hp.add(buttonCancel);
		hp.setSpacing(2);
		hp.setCellHorizontalAlignment(buttonSubmit, HasHorizontalAlignment.ALIGN_RIGHT);
		hp.setCellHorizontalAlignment(buttonCancel, HasHorizontalAlignment.ALIGN_LEFT);

		panel.add(hp);
		
		// Add an event handler to the form.
		uploadForm.addSubmitHandler(new FormPanel.SubmitHandler() {
			@Override
			public void onSubmit(SubmitEvent event) {
				// This event is fired just before the form is submitted. We can
				// take this opportunity to perform validation.
			}
		});

	    uploadForm.addSubmitCompleteHandler(submitCompleteHandler);

		this.add(uploadForm);
	}

}
