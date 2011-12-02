package com.reverbin.ODA.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.dom.client.Element;
import com.google.gwt.user.client.History;
import com.google.gwt.event.logical.shared.ResizeEvent;
import com.google.gwt.event.logical.shared.ResizeHandler;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.user.client.ui.*;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.DOM;
import com.reverbin.ODA.shared.Endian;
import com.reverbin.ODA.shared.PlatformDescriptor;
import com.reverbin.ODA.shared.PlatformId;
import com.google.gwt.http.client.*;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.Window;

/* Things to do
 * 
 * TODO: Add close button to upload file form
 * TODO: Implement strings processing
 * TODO: Limit binary size
 * TODO: Add PayPal donate button
 * TODO: Display status of binary on Assembly tab (file type, size, arch, etc.)
 */

public class Main implements EntryPoint, SubmitCompleteHandler,  ValueChangeHandler<String> {
	TabPanel tabPanel = new TabPanel();
	FlowPanel asmPanel = new FlowPanel();
	FlowPanel platformPanel = new FlowPanel();
	StatusIndicator statusIndicator;
	ModelPlatformBin modelPlatformBin = new ModelPlatformBin();
	ViewHex viewHex;
	ViewAssembly viewAsm;
	ViewStrings viewStrings;
	ViewSections viewSections;
	ViewSymbols viewSymbols;
	HexInput hexInput = new HexInput(modelPlatformBin);
	UploadFile uploadFile = new UploadFile(this);
	DialogHelp dialogHelp = new DialogHelp();
	final FlowPanel flowpanel = new FlowPanel();
	final static int MIN_DIS_DISPLAY_SIZE = 150;
	final static int MIN_DIS_DISPLAY_MARGIN = 50;

	/**
	 * Fired when a form has been submitted successfully.
	 * 
	 * @param event
	 *            the event
	 */
	public void onSubmitComplete(SubmitCompleteEvent event) {
		uploadFile.hide();
		modelPlatformBin.setBytes(HexUtils.textToBytes(event.getResults()));
		// tabPanel.selectTab(0);
	}

	public void onModuleLoad() {

         RootPanel rp = RootPanel.get();        
         VerticalPanel vpanel = new VerticalPanel();
            
         // file
         MenuBar menuBarFile = new MenuBar(true);
         menuBarFile.addItem("Upload File", new Command() {
             public void execute() {
            	 uploadFile.center();
            	 uploadFile.show();
             }
         });
                
         // examples
         MenuBar menuBarExamples = new MenuBar(true);
         menuBarExamples.addItem("strcpy (x86)", new Command() {
        	 public void execute() 
        	 {
                 PlatformDescriptor platform = new PlatformDescriptor();
                 platform.baseAddress = 0;
                 platform.endian = Endian.LITTLE;
                 platform.platformId = PlatformId.X86;
        		 loadExample("strcpy.x86.hex", platform);
        	 }
         });
         menuBarExamples.addItem("strcpy (arm)", new Command() {
        	 public void execute() 
        	 {
                 PlatformDescriptor platform = new PlatformDescriptor();
                 platform.baseAddress = 0;
                 platform.endian = Endian.LITTLE;
                 platform.platformId = PlatformId.ARM;
        		 loadExample("strcpy.arm.hex", platform);
        	 }
         });
         
         // help
         MenuBar menuBarHelp = new MenuBar(true);
         menuBarHelp.addItem("About", new Command() {
             public void execute() {
            	 dialogHelp.center();
            	 dialogHelp.show();
             }
         });
         
         // top-level menu bar
         MenuBar menu = new MenuBar(false);
         menu.addItem("File", menuBarFile);
         menu.addItem("Examples", menuBarExamples);
         menu.addItem("Help", menuBarHelp);
         
         //http://icons.mysitemyway.com/wp-content/gallery/matte-blue-and-white-square-icons-business/116958-matte-blue-and-white-square-icon-business-gear2.png
         // plain gear: http://dsmy2muqb7t4m.cloudfront.net/tuts/169_Settings_Icon/step8a.jpg
         Image image = new Image("images/oda.png");
         Image busyImage = new Image("images/oda.gif");
         
         viewHex = new ViewHex(modelPlatformBin);
         tabPanel.add(viewHex, "Hex");
         statusIndicator = new StatusIndicator(busyImage);
         viewAsm = new ViewAssembly(modelPlatformBin, statusIndicator);
         asmPanel.add(viewAsm);
         asmPanel.setWidth("600px");
         //asmPanel.setHeight("600px");
         tabPanel.add(asmPanel, "Assembly");
         tabPanel.addSelectionHandler(viewAsm);

         // strings tab
         viewStrings = new ViewStrings(modelPlatformBin, statusIndicator);
         viewStrings.setWidth("600px");
         //viewStrings.setHeight("418px");
         tabPanel.add(viewStrings, "Strings");
         tabPanel.addSelectionHandler(viewStrings);

         // sections tab
         viewSections = new ViewSections(modelPlatformBin, statusIndicator);
         viewSections.setWidth("600px");
         viewSections.setHeight("418px");
         tabPanel.add(viewSections, "Sections");
         tabPanel.addSelectionHandler(viewSections);
         
         // symbols tab
         viewSymbols = new ViewSymbols(modelPlatformBin, statusIndicator);
         viewSymbols.setWidth("600px");
         viewSymbols.setHeight("418px");
         tabPanel.add(viewSymbols, "Symbols");
         tabPanel.addSelectionHandler(viewSymbols);
                  
         //panel.setSize("739px", "538px");
         tabPanel.addStyleName("table-center");
         
         AbsolutePanel absPanel = new AbsolutePanel();
         absPanel.setSize("128px", "128px");
         HorizontalPanel hp = new HorizontalPanel();     
         hp.setWidth("100%");
         busyImage.setSize("128px", "128px");
         image.setSize("128px", "128px");
         absPanel.add(image, 0, 0);
         absPanel.add(busyImage, 0, 0);
         hp.add(absPanel);
         hp.setCellHorizontalAlignment(absPanel, HasHorizontalAlignment.ALIGN_RIGHT);
         //hp.setCellWidth(absPanel, "25%");

         Image logo = new Image("images/oda_logo4.png");
         hp.add(logo);
         hp.setCellHorizontalAlignment(logo, HasHorizontalAlignment.ALIGN_CENTER);
         hp.setCellVerticalAlignment(logo, HasVerticalAlignment.ALIGN_MIDDLE);
         
         PayPalPanel ppp = new PayPalPanel();
         Anchor contact = new Anchor("Contact Us!");
         contact.setHref("mailto:admin@onlinedisassembler.com");
         contact.addStyleName("contact");
         VerticalPanel vpPaypalContact = new VerticalPanel();
         vpPaypalContact.add(ppp);
         vpPaypalContact.add(contact);
         vpPaypalContact.setCellHeight(contact, "32px");
         vpPaypalContact.setCellHorizontalAlignment(contact, HasHorizontalAlignment.ALIGN_CENTER);
         vpPaypalContact.setCellVerticalAlignment(contact, HasVerticalAlignment.ALIGN_BOTTOM);
         hp.add(vpPaypalContact);
         hp.setCellHorizontalAlignment(vpPaypalContact, HasHorizontalAlignment.ALIGN_LEFT);
         hp.setCellVerticalAlignment(vpPaypalContact, HasVerticalAlignment.ALIGN_MIDDLE);
         


         vpanel.add(hp);
         vpanel.add(menu);
         vpanel.add(tabPanel);
         vpanel.setSpacing(5);
         vpanel.addStyleName("centered");
         
         /* using a flow panel here coupled with the "centered" CSS I added
            makes the interface centered */         
         flowpanel.add(vpanel);

         flowpanel.setHeight(Window.getClientHeight() + "px");
         Window.addResizeHandler(new ResizeHandler() {
        	 public void onResize(ResizeEvent event) {
        		 int height = event.getHeight();
        		 flowpanel.setHeight(height + "px");
        	 }
         });
         
         rp.add(flowpanel);
         
         PlatformDescriptor platform = new PlatformDescriptor();
         platform.baseAddress = 0;
         platform.endian = Endian.LITTLE;
         platform.platformId = PlatformId.X86;
         
         loadExample("strcpy.x86.hex", platform);
         statusIndicator.setBusy(true);
         
		// If the application starts with no history token, redirect to a new
		// 'baz' state.
		String initToken = History.getToken();
		if (initToken.length() == 0) {
		  History.newItem("disoff_0");
		}
		
		 // Add history listener
		 History.addValueChangeHandler(this);
		
		 // Now that we've setup our listener, fire the initial history state.
		 History.fireCurrentHistoryState();
         
         
         
    }


	/**
	 * Load example binaries
	 * 
	 * @param example
	 * @param platform
	 */
	private void loadExample(String example, final PlatformDescriptor platform) {
		/*
		 * Because the RequestBuilder class doesn't handle GET results that are
		 * content-type application/octet-stream, I ended up storing the
		 * examples in ASCII hex, which then gets converted into binary via
		 * HexUtils. Not ideal, but it works.
		 */
		RequestBuilder req = new RequestBuilder(RequestBuilder.GET, "examples/"
				+ example);
		try {
			req.sendRequest("", new RequestCallback() {
				@Override
				public void onResponseReceived(Request req, Response resp) {
					modelPlatformBin.setPlatformBin(platform,
							HexUtils.textToBytes(resp.getText()));
					tabPanel.selectTab(1);
				}

				@Override
				public void onError(Request res, Throwable throwable) {
				}
			});
		} catch (Exception e) {

		}
	}

	/**
	 * Update disassembly when hex bytes change
	 */
	public void updateHex(byte[] hexBytes) {
		// hexView.setRawBytes(hexBytes);
		// formatterService.formatHex(asmView.getPlatform(), hexBytes,
		// hexCallback);
	}

	/**
	 * Update disassembly when platform changes
	 */
	public void updatePlatform(PlatformDescriptor platform) {
		// asmView.setPlatform(platform);
		// formatterService.formatHex(platform, hexView.getRawBytes(),
		// hexCallback);
	}

	public void updateHexAndPlatform(byte[] hexBytes,
			PlatformDescriptor platform) {
		// hexView.setRawBytes(hexBytes);
		// asmView.setPlatform(platform);
		// formatterService.formatHex(platform, hexBytes, hexCallback);
	}
	
	@Override
	public void onValueChange(ValueChangeEvent<String> event) {
		// Handle History Events including back button of the browser
		String eventString = event.getValue();
		
		// Events are coded with the name of the widget followed by a unique id 
		if (eventString.substring(0,7).equals("disoff_") ) {
			// Disassembly View event
			//	Here we're emulating following links to anchors in the disassembly
			//	such as branch instructions. Anchors use the hex address as their
			//	unique id
			Element element = DOM.getElementById(eventString.substring(7));
			if ( element != null ) {
				// Get the offset in pixels of the anchor to be traveled to
				int scrollPosition = element.getOffsetTop();
				
				// Set the view asm's scroll position so that the anchor is
				//	in view.
				viewAsm.scrollPanel.setVerticalScrollPosition(scrollPosition);
			}
		}
	}

}
