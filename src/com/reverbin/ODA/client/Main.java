package com.reverbin.ODA.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.*;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.Window;
import com.reverbin.ODA.shared.FormattedOutput;
import com.reverbin.ODA.shared.PlatformDescriptor;
import com.google.gwt.http.client.*;

public class Main implements EntryPoint, ViewUpdater {
	TabPanel tabPanel = new TabPanel();
    HTML htmlDisplay = new HTML("", true);
    HTML stringsDisplay = new HTML("", true);
    String hexHtml = "";
    String assHtml = "";
    TextArea hexArea = new TextArea();
    ViewAssembly asmView = new ViewAssembly(this, htmlDisplay);
    ViewHex hexView = new ViewHex(this, hexArea);
    FlowPanel asmPanel = new FlowPanel();
    FlowPanel platformPanel = new FlowPanel();
    FlowPanel hexHeaderPanel = new FlowPanel();
    FlowPanel hexPanel = new FlowPanel();
    FlowPanel stringsPanel = new FlowPanel();
    
	private final HexFormatterServiceAsync formatterService = HexFormatterService.Util.getInstance();

	AsyncCallback<FormattedOutput> hexCallback = new AsyncCallback<FormattedOutput>(){

	    @Override
	    public void onFailure(Throwable caught) {
	        //hexInput.hide();
	        //htmlDisplay.setHTML("Failed to get hex");
	    }

	    @Override
	    public void onSuccess(FormattedOutput result) {
	    	hexInput.hide();
	    	asmView.setText(result.getFormattedAssembly());
	    	hexView.setText(result.getFormattedHex());
	    	stringsDisplay.setHTML(result.getFormattedStrings());
	        Main.this.updateOutputDisplay();        
	    	
	    }};
	    
	    HexInput hexInput = new HexInput(this);
	    UploadFile uploadFile = new UploadFile();
    
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
        		 loadExample("strcpy.x86.hex", new PlatformDescriptor("x86"));
        	 }
         });
         menuBarExamples.addItem("strcpy (arm)", new Command() {
        	 public void execute() 
        	 {
        		 loadExample("strcpy.arm.hex", new PlatformDescriptor("ARM"));
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
         
         // hex tab
         Button hexSubmit = new Button("Disassemble");
         hexSubmit.addClickHandler(new ClickHandler() {
 			public void onClick(ClickEvent event) 
 			{	
 				updateHex(HexUtils.parseText(hexArea.getText()));
 				
 			}
 		 });
         hexHeaderPanel.add(hexSubmit);
         hexHeaderPanel.setStyleName("panelBox");
         int clientHeight = Window.getClientHeight();
         hexArea.setSize("574px", "" + (int) (clientHeight*2/3) + "px");
         hexArea.setStyleName("textarea");
         hexPanel.add(hexHeaderPanel);
         hexPanel.add(hexArea);
         hexPanel.setSize("600px", "" + (int) (clientHeight*2/3 + 82) + "px" );
         tabPanel.add(hexPanel, "Hex");

         // disassembly tab
         VerticalPanel asmHeaderVp = new VerticalPanel();
         asmHeaderVp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
         
         ListBox listBoxPlatform = new ListBox();
         listBoxPlatform.addItem("x86");
         listBoxPlatform.addItem("ARM");
         listBoxPlatform.addItem("MIPS");
         listBoxPlatform.addItem("PowerPC");
         listBoxPlatform.setVisibleItemCount(1);
         listBoxPlatform.addChangeHandler(asmView);
         
         ListBox listBoxEndian = new ListBox();
         listBoxEndian.addItem("BIG");
         listBoxEndian.addItem("LIL");
         listBoxEndian.setVisibleItemCount(1);
         
         HorizontalPanel hp = new HorizontalPanel();   
         hp.setSpacing(3);
         hp.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
         hp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
         hp.add(new Label("Platform"));
         hp.add(listBoxPlatform);
         hp.add(new Label("     "));
         hp.add(new Label("Endian"));
         hp.add(listBoxEndian);
         asmHeaderVp.add(hp);
         
         hp = new HorizontalPanel();
         hp.setSpacing(3);
         hp.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
         hp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
         hp.add(new Label("Base Address"));
         TextBox textBoxBase = new TextBox();
         textBoxBase.setVisibleLength(8);
         hp.add(textBoxBase);
         
         asmHeaderVp.add(hp);
         
         platformPanel.add(asmHeaderVp);
         platformPanel.setStyleName("panelBox");

         asmPanel.add(platformPanel);      
         asmPanel.add(htmlDisplay);
         asmPanel.setSize("600px", "418px");
         tabPanel.add(asmPanel, "Assembly");

         // strings tab
         stringsPanel.add(stringsDisplay);
         stringsPanel.setSize("600px", "418px");
         tabPanel.add(stringsPanel, "Strings");

         //panel.setSize("739px", "538px");
         tabPanel.addStyleName("table-center");
         
         hp = new HorizontalPanel();       
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
         
         /* Uncomment to add NORTH and WEST panels */
         /*
         FlowPanel northPanel = new FlowPanel();
         northPanel.add(new HTML("<center><H1>DockLayoutPanel North</H1></center>"));
         northPanel.setStyleName("northPanelStyle");
         
         FlowPanel westPanel = new FlowPanel();
         westPanel.add(new HTML("<H3>DockLayoutPanel West</H3>"));
         westPanel.setStyleName("westPanelStyle");
         
         DockLayoutPanel p = new DockLayoutPanel(Unit.EM);   
         p.addNorth(northPanel, 6);
         p.addWest(westPanel, 20);
         p.add(vpanel);
         
         rp.add(p);
         */
         
         /* using a flow panel here coupled with the "centered" CSS I added
            makes the interface centered */
         FlowPanel flowpanel = new FlowPanel();
         flowpanel.add(vpanel);
         
         rp.add(flowpanel);
        
         loadExample("strcpy.x86.hex", new PlatformDescriptor("x86"));
    }

    protected void updateOutputDisplay() 
    {
    	final int PADDING = 20;
    	
    	tabPanel.selectTab(2);
    	stringsPanel.setHeight("" + (stringsDisplay.getOffsetHeight()+ PADDING) + "px");
    	
    	tabPanel.selectTab(1);
    	// resize the height of the assembly panel to fit the displayed code
    	asmPanel.setHeight("" + (htmlDisplay.getOffsetHeight() + platformPanel.getOffsetHeight() + PADDING) + "px");
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
	        		  updateHexAndPlatform(HexUtils.parseText(resp.getText()), platform);
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
		hexView.setRawBytes(hexBytes);
	    formatterService.formatHex(asmView.getPlatform(), hexBytes, hexCallback);	
	}
	
	/**
	 * Update disassembly when platform changes
	 */
	public void updatePlatform(PlatformDescriptor platform)
	{
		asmView.setPlatform(platform);
	    formatterService.formatHex(platform, hexView.getRawBytes(), hexCallback);	
	}
	
	public void updateHexAndPlatform(byte[] hexBytes, PlatformDescriptor platform)
	{
		hexView.setRawBytes(hexBytes);
		asmView.setPlatform(platform);
	    formatterService.formatHex(platform, hexBytes, hexCallback);	
	}
}
