package com.reverbin.ODA.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.*;
import com.google.gwt.user.client.Command;
import com.reverbin.ODA.shared.FormattedOutput;
import com.reverbin.ODA.shared.PlatformDescriptor;

public class Main implements EntryPoint, ViewUpdater {
	TabPanel tabPanel = new TabPanel();
    HTML htmlDisplay = new HTML("", true);
    String hexHtml = "";
    String assHtml = "";
    TextArea hexArea = new TextArea();
    ViewAssembly asmView = new ViewAssembly(this, htmlDisplay);
    ViewHex hexView = new ViewHex(this, hexArea);
    final byte[] DEFAULT_HEX_BYTES = {0x31, (byte) 0xed, 0x5e, (byte)0x89, (byte)0xe1, (byte)0x83, (byte)0xe4, (byte)0xf0, 0x50, 0x54, 0x52, 0x68, 0x10, (byte)0xa0, 0x05, 0x08};
    FlowPanel asmPanel = new FlowPanel();
    FlowPanel platformPanel = new FlowPanel();
    FlowPanel hexHeaderPanel = new FlowPanel();
    FlowPanel hexPanel = new FlowPanel();
    
	private final HexFormatterServiceAsync formatterService = HexFormatterService.Util.getInstance();

	AsyncCallback<FormattedOutput> hexCallback = new AsyncCallback<FormattedOutput>(){

	    @Override
	    public void onFailure(Throwable caught) {
	        //hexInput.hide();
	        //htmlDisplay.setHTML("Failed to get hex");
	    }

	    @Override
	    public void onSuccess(FormattedOutput result) {
	    	/*
	        hexInput.hide();
	        tabPanel.selectTab(1);
	        hexHtml = result.getFormattedHex();
	        assHtml = result.getFormattedAssembly();
	        */
	    	
	    	hexInput.hide();
	    	asmView.setText(result.getFormattedAssembly());
	    	hexView.setText(result.getFormattedHex());
	    	tabPanel.selectTab(1);
	        Main.this.updateOutputDisplay();
	        
	    	
	    }};
	    
	    HexInput hexInput = new HexInput(this);
    
    public void onModuleLoad() {

         RootPanel rp = RootPanel.get();        
         VerticalPanel vpanel = new VerticalPanel();
            
         // file
         MenuBar menuBarFile = new MenuBar(true);
         menuBarFile.addItem("Upload File", (Command) null);        
         MenuItem menuItemInputHex = new MenuItem("Input Hex", false, new Command() {
             public void execute() {
                 hexInput.setText("");
                 hexInput.setHTML("Hex Input");
                 hexInput.center();
                 hexInput.show();
             }
         });
         menuBarFile.addItem(menuItemInputHex);
        
         // edit
         MenuBar menuBarEdit = new MenuBar(true);
         menuBarEdit.addItem("Cut", (Command) null);
         menuBarEdit.addItem("Copy", (Command) null);
         menuBarEdit.addItem("Paste", (Command) null);
         
         // help
         MenuBar menuBarHelp = new MenuBar(true);
         menuBarHelp.addItem("About", (Command) null);
         
         // top-level menu bar
         MenuBar menu = new MenuBar(false);
         menu.addItem("File", menuBarFile);
         menu.addItem("Edit", menuBarEdit);
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
         //hexArea.setSize("500px", "" + hexHeaderPanel.getOffsetWidth() + "px");
         //hexArea.setSize("600px", "" + hexHeaderPanel.getOffsetWidth() + "px");
         hexArea.setSize("574px", "336px");
         hexArea.setStyleName("textarea");
         hexPanel.add(hexHeaderPanel);
         hexPanel.add(hexArea);
         hexPanel.setSize("600px", "418px");
         tabPanel.add(hexPanel, "Hex");

         // disassembly tab
         ListBox listBox = new ListBox();
         listBox.addItem("x86");
         listBox.addItem("ARM");
         listBox.addItem("MIPS");
         listBox.addItem("PowerPC");
         listBox.setVisibleItemCount(1);
         listBox.addChangeHandler(asmView);
         
         HorizontalPanel hp = new HorizontalPanel();     
         hp.add(new Label("Platform"));
         hp.add(listBox);
         hp.setSpacing(5);
         platformPanel.add(hp);
         platformPanel.setStyleName("panelBox");

         asmPanel.add(platformPanel);      
         asmPanel.add(htmlDisplay);
         asmPanel.setSize("600px", "418px");
         tabPanel.add(asmPanel, "Assembly");

         FlowPanel flowpanel = new FlowPanel();
         flowpanel.add(new Label("012345\nabcdef"));
         flowpanel.setSize("600px", "418px");
         tabPanel.add(flowpanel, "Strings");

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
         flowpanel = new FlowPanel();
         flowpanel.add(vpanel);
         
         rp.add(flowpanel);
        
         this.updateHex(DEFAULT_HEX_BYTES);         
    }

    protected void updateOutputDisplay() 
    {
    	final int PADDING = 20;
    	
    	// resize the height of the assembly panel to fit the displayed code
    	asmPanel.setHeight("" + (htmlDisplay.getOffsetHeight() + platformPanel.getOffsetHeight() + PADDING) + "px");
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
}
