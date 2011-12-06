package com.reverbin.ODA.client;

import com.google.gwt.core.client.Scheduler;
import com.google.gwt.core.client.Scheduler.ScheduledCommand;
import com.google.gwt.event.logical.shared.ResizeEvent;
import com.google.gwt.event.logical.shared.ResizeHandler;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.reverbin.ODA.shared.DisassemblyOutput;

public class ViewSections extends VerticalPanel implements SelectionHandler<Integer>{
	
	VerticalPanel scrollContainer;
	ScrollPanel scrollPanel;
	StatusIndicator statusIndicator;
	HTML html = new HTML();
	final int PANEL_PADDING = 10;
		
	public ViewSections(ModelPlatformBin mpb, StatusIndicator si)
	{
		statusIndicator = si;

		// Initialize HTML text
		html.setHTML("<pre><insn>No sections found</insn></pre");
		html.setWidth("600px");
		
		// Create the Window Layout
		scrollPanel = new ScrollPanel();
		scrollContainer = new VerticalPanel();
		scrollContainer.add(html);
		scrollContainer.setHeight("" + (html.getOffsetHeight() + PANEL_PADDING) + "px");
		scrollPanel.add(scrollContainer);
		this.add(scrollPanel);
		this.setSpacing(this.PANEL_PADDING);
		
		resize();
		
		Window.addResizeHandler(new ResizeHandler() {
       	 public void onResize(ResizeEvent event) {
       		 resize();
       	 }
        });
	}
	
	public void updateHtml(DisassemblyOutput disOutput)
	{
		html.setHTML(disOutput.getSectionHtml());
		
		// Deferring the resize event will get the proper offsetHeight
		//	if the tab is already selected. This works in concert with 
		//	the onSelected tab to make sure the widget gets properly
		//	sized.
		Scheduler.get().scheduleDeferred(new ScheduledCommand() {
			@Override
			public void execute() {
				// Get and work with the element's offsetHeight.
				resize();
			}
		});
	}
	
	private void resize()
	{
    	int remainingSpace = Window.getClientHeight() - scrollPanel.getAbsoluteTop();
    	int requiredSpace = html.getOffsetHeight() + this.PANEL_PADDING*2;
    	if ( remainingSpace > requiredSpace )
    	{
        	scrollPanel.setHeight( requiredSpace + "px");    		    		
    	}
    	else if ( remainingSpace < Main.MIN_DIS_DISPLAY_SIZE )
    	{
        	scrollPanel.setHeight( Main.MIN_DIS_DISPLAY_SIZE - Main.MIN_DIS_DISPLAY_MARGIN + "px");    		
    	}
    	else
    	{
    		scrollPanel.setHeight( remainingSpace - Main.MIN_DIS_DISPLAY_MARGIN + "px");
    	}
	}
	
	// Need this because getOffsetHeight doesn't return an accurate
	//	value until after the DOM has been updated. This will size
	//	the tab once it has been selected.
	@Override
	public void onSelection(SelectionEvent<Integer> event) {
		//TODO: get rid of hard-coded value here
		if (event.getSelectedItem() == Main.TAB_INDEX_SECTIONS) {
			resize();		
		}
	}
}
