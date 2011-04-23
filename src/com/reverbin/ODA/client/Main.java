package com.reverbin.ODA.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.*;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.Window;
import com.reverbin.ODA.shared.Endian;
import com.reverbin.ODA.shared.PlatformDescriptor;
import com.reverbin.ODA.shared.PlatformId;
import com.google.gwt.http.client.*;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

/* Things to do
 * 
 * TODO: Add close button to upload file form
 * TODO: Implement strings processing
 * TODO: Limit binary size
 */

public class Main implements EntryPoint, SubmitCompleteHandler {
	TabPanel tabPanel = new TabPanel();
    FlowPanel asmPanel = new FlowPanel();
    FlowPanel platformPanel = new FlowPanel();
    StatusIndicator statusIndicator;
    ModelBinary modelBinary = new ModelBinary();
    ModelPlatform modelPlatform = new ModelPlatform();
    ViewHex viewHex;
    ViewAssembly viewAsm;
    ViewStrings viewStrings;
    HexInput hexInput = new HexInput(modelBinary);
    UploadFile uploadFile = new UploadFile(this);
    DialogHelp dialogHelp = new DialogHelp();
	
    /**
     * Fired when a form has been submitted successfully.
     *
     * @param event the event
     */
	public void onSubmitComplete(SubmitCompleteEvent event)
    {
		modelBinary.setBytes(HexUtils.textToBytes(event.getResults()));
    	tabPanel.selectTab(0);
    	uploadFile.hide();
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
         
         MenuItem menuItemInputHex = new MenuItem("Input Hex", false, new Command() {
             public void execute() {
                 hexInput.setText("");
                 hexInput.setHTML("Hex Input");
                 hexInput.center();
                 hexInput.show();
             }
         });
         //menuBarFile.addItem(menuItemInputHex);
        
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
         Image image = new Image("images/oda.png");
         Image busyImage = new Image("images/oda.gif");
         
         viewHex = new ViewHex(modelBinary);
         tabPanel.add(viewHex, "Hex");
         statusIndicator = new StatusIndicator(busyImage);
         viewAsm = new ViewAssembly(modelBinary, modelPlatform, statusIndicator);
         asmPanel.add(new ViewPlatformSelection(modelPlatform));      
         asmPanel.add(viewAsm);
         asmPanel.setSize("600px", "418px");
         tabPanel.add(asmPanel, "Assembly");

         // strings tab
         viewStrings = new ViewStrings(modelBinary, statusIndicator);
         viewStrings.setSize("600px", "418px");
         tabPanel.add(viewStrings, "Strings");
         tabPanel.addSelectionHandler(viewStrings);

         //panel.setSize("739px", "538px");
         tabPanel.addStyleName("table-center");
         
         AbsolutePanel absPanel = new AbsolutePanel();
         absPanel.setSize("128px", "128px");
         HorizontalPanel hp = new HorizontalPanel();       
         absPanel.add(image, 0, 0);
         absPanel.add(busyImage, 0, 0);
         hp.add(absPanel);
         hp.setCellHorizontalAlignment(image, HasHorizontalAlignment.ALIGN_CENTER);
         image.setSize("128px", "128px");
         busyImage.setSize("128px", "128px");

         hp.add(new HTML("<H1>ODA Online Disassembler</H1>"));

         vpanel.add(hp);
         vpanel.add(menu);
         vpanel.add(tabPanel);
         vpanel.setSpacing(5);
         vpanel.addStyleName("centered");
         
         /* using a flow panel here coupled with the "centered" CSS I added
            makes the interface centered */
         FlowPanel flowpanel = new FlowPanel();
         flowpanel.add(vpanel);
         
         rp.add(flowpanel);
         
         PlatformDescriptor platform = new PlatformDescriptor();
         platform.baseAddress = 0;
         platform.endian = Endian.LITTLE;
         platform.platformId = PlatformId.X86;
         
         loadExample("strcpy.x86.hex", platform);
         statusIndicator.setBusy(true);
    }
    
    /**
     * Load example binaries
     * 
     * @param example
     * @param platform
     */
    private void loadExample(String example, final PlatformDescriptor platform)
    {
    	/* Because the RequestBuilder class doesn't handle GET results that are content-type
    	 * application/octet-stream, I ended up storing the examples in ASCII hex, which then
    	 * gets converted into binary via HexUtils.  Not ideal, but it works.
    	 */
        RequestBuilder req = new RequestBuilder(RequestBuilder.GET, "examples/" + example);
        try
        {
	         req.sendRequest("", new RequestCallback() {
	        	  @Override
	        	  public void onResponseReceived(Request req, Response resp) {
	        		  modelBinary.setBytes(HexUtils.textToBytes(resp.getText()));
	        		  modelPlatform.setPlatform(platform);
	        		  tabPanel.selectTab(1);
	        	  }
	
	        	  @Override
	        	  public void onError(Request res, Throwable throwable) {
	        		  String s = res.toString();
	        	    // handle errors
	        	  }
	        	});
        }
        catch (Exception e)
        {
       	 
        } 
    }
    
    /**
     * Update disassembly when hex bytes change
     */
	public void updateHex(byte[] hexBytes)
	{
		//hexView.setRawBytes(hexBytes);
	    //formatterService.formatHex(asmView.getPlatform(), hexBytes, hexCallback);	
	}
	
	/**
	 * Update disassembly when platform changes
	 */
	public void updatePlatform(PlatformDescriptor platform)
	{
		//asmView.setPlatform(platform);
	    //formatterService.formatHex(platform, hexView.getRawBytes(), hexCallback);	
	}
	
	public void updateHexAndPlatform(byte[] hexBytes, PlatformDescriptor platform)
	{
		//hexView.setRawBytes(hexBytes);
		//asmView.setPlatform(platform);
	    //formatterService.formatHex(platform, hexBytes, hexCallback);	
	}
}
