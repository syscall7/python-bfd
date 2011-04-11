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

public class Main implements EntryPoint, ViewUpdater, SubmitCompleteHandler {
	TabPanel tabPanel = new TabPanel();
    HTML stringsDisplay = new HTML("", true);
    FlowPanel asmPanel = new FlowPanel();
    FlowPanel platformPanel = new FlowPanel();
    FlowPanel stringsPanel = new FlowPanel();
    ModelBinary modelBinary = new ModelBinary();
    ModelPlatform modelPlatform = new ModelPlatform();
    ViewHex viewHex = new ViewHex(modelBinary);
    ViewAssembly viewAsm = new ViewAssembly(modelBinary, modelPlatform);
    HexInput hexInput = new HexInput(modelBinary);
    UploadFile uploadFile = new UploadFile(this);
	    
    /**
     * Fired when a form has been submitted successfully.
     *
     * @param event the event
     */
	public void onSubmitComplete(SubmitCompleteEvent event)
    {
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
         menuBarFile.addItem(menuItemInputHex);
        
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
         menuBarHelp.addItem("About", (Command) null);
         
         // top-level menu bar
         MenuBar menu = new MenuBar(false);
         menu.addItem("File", menuBarFile);
         menu.addItem("Examples", menuBarExamples);
         menu.addItem("Help", menuBarHelp);
         
         tabPanel.add(viewHex, "Hex");

         asmPanel.add(new ViewPlatformSelection(modelPlatform));      
         asmPanel.add(viewAsm);
         asmPanel.setSize("600px", "418px");
         tabPanel.add(asmPanel, "Assembly");

         // strings tab
         stringsPanel.add(stringsDisplay);
         stringsPanel.setSize("600px", "418px");
         tabPanel.add(stringsPanel, "Strings");

         //panel.setSize("739px", "538px");
         tabPanel.addStyleName("table-center");
         
         HorizontalPanel hp = new HorizontalPanel();       
         //http://icons.mysitemyway.com/wp-content/gallery/matte-blue-and-white-square-icons-business/116958-matte-blue-and-white-square-icon-business-gear2.png
         Image image = new Image("images/oda.png");
         hp.add(image);
         hp.setCellHorizontalAlignment(image, HasHorizontalAlignment.ALIGN_CENTER);
         image.setSize("128px", "128px");
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
    }

    protected void updateOutputDisplay() 
    {
    	final int PADDING = 20;
    	
    	tabPanel.selectTab(2);
    	stringsPanel.setHeight("" + (stringsDisplay.getOffsetHeight()+ PADDING) + "px");
    	
    	tabPanel.selectTab(1);
    	// resize the height of the assembly panel to fit the displayed code
    	asmPanel.setHeight("" + (viewAsm.getOffsetHeight() + platformPanel.getOffsetHeight() + PADDING) + "px");
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
