package com.reverbin.ODA.client;

import com.google.gwt.core.client.EntryPoint;
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

         RootLayoutPanel rp = RootLayoutPanel.get();        
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
             
         FlowPanel flowpanel = new FlowPanel();
         
         // hex tab
         hexArea.setSize("519px", "414px");
         flowpanel.add(hexArea);
         flowpanel.setSize("524px", "418px");
         tabPanel.add(flowpanel, "Hex");

         // disassembly tab
         flowpanel = new FlowPanel();
         ListBox listBox = new ListBox();
         listBox.addItem("x86");
         listBox.addItem("ARM");
         listBox.addItem("MIPS");
         listBox.addItem("PowerPC");
         listBox.setVisibleItemCount(1);
         listBox.addChangeHandler(asmView);
         
         FlowPanel platformPanel = new FlowPanel();
         
         HorizontalPanel hp = new HorizontalPanel();     
         hp.add(new Label("Platform"));
         hp.add(listBox);
         hp.setSpacing(5);
         platformPanel.add(hp);
         platformPanel.setStyleName("panelBox");

         flowpanel.add(platformPanel);      
         flowpanel.add(htmlDisplay);
         flowpanel.setSize("524px", "418px");
         tabPanel.add(flowpanel, "Assembly");

         flowpanel = new FlowPanel();
         flowpanel.add(new Label("012345\nabcdef"));
         flowpanel.setSize("524px", "418px");
         tabPanel.add(flowpanel, "Strings");

         tabPanel.selectTab(0);
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
        
        
    }

    protected void updateOutputDisplay() {
        //htmlDisplay.setHTML(assHtml);
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
