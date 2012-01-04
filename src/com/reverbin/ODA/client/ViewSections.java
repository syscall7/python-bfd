package com.reverbin.ODA.client;


import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;

import com.google.gwt.core.client.Scheduler;
import com.google.gwt.core.client.Scheduler.ScheduledCommand;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.logical.shared.ResizeEvent;
import com.google.gwt.event.logical.shared.ResizeHandler;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.ScrollPanel;
import com.google.gwt.user.client.ui.TabPanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.reverbin.ODA.shared.CodeSection;
import com.reverbin.ODA.shared.DisassemblyOutput;
import com.reverbin.ODA.shared.PlatformDescriptor;

public class ViewSections extends VerticalPanel implements SelectionHandler<Integer>, ClickHandler{
	
	VerticalPanel scrollContainer;
	ScrollPanel scrollPanel;
	StatusIndicator statusIndicator;
	HTML html = new HTML();
	FlexTable sectionTable = new FlexTable();
	final int PANEL_PADDING = 10;
	ModelPlatformBin mpb;
	TabPanel rent;
	HashMap<Integer, CodeSection> sections;
		
	public ViewSections(ModelPlatformBin m, StatusIndicator si, TabPanel parent)
	{
		this.mpb = m;
		statusIndicator = si;
			
		// Initialize HTML text
		html.setHTML("<pre><insn>No sections found</insn></pre");
		html.setWidth("600px");
		sectionTable.setWidget(0, 0, html);
		
		// Create the Window Layout
		scrollPanel = new ScrollPanel();
		scrollPanel.add(sectionTable);
		this.add(scrollPanel);
		this.setSpacing(this.PANEL_PADDING);
		this.rent = parent;
	}
	
	public void updateHtml(DisassemblyOutput disOutput)
	{
		sections = disOutput.getSections();
		
		sectionTable.removeAllRows();
		
		if ((sections != null) && (sections.size() > 0))
		{
			int row = 0;
			
			sectionTable.insertRow(0);
			sectionTable.getRowFormatter().addStyleName(0,"FlexTable-Header");
		    
			sectionTable.setText(0, 0, "Index");
			sectionTable.setText(0, 1, "Name");
			sectionTable.setText(0, 2, "Size");
			sectionTable.setText(0, 3, "Address");
			sectionTable.setText(0, 4, "Alignment");
			sectionTable.setText(0, 5, "Flags");
			//sectionTable.getRowFormatter().addStyleName(0,"FlexTable-ColumnLabelCell");
		    row++;
		    
	    	ArrayList<Integer> sortedKeys=new ArrayList<Integer>(sections.keySet());
	    	Collections.sort(sortedKeys);
	    	for (int index : sortedKeys)
			{
				CodeSection s = sections.get(index);
	    		Anchor a = new Anchor(s.name);
	    		a.addClickHandler(this);
	    		a.setName(Integer.toString(index));
	    		
				sectionTable.setText(row, 0, s.index.toString());
				sectionTable.setWidget(row, 1, a);
				sectionTable.setText(row, 2, s.size.toString());
				sectionTable.setText(row, 3, "0x" + Integer.toHexString(s.vma));
				sectionTable.setText(row, 4, s.alignment.toString());
				sectionTable.setText(row, 5, s.flags);
				if ((row % 2) == 1)
					sectionTable.getRowFormatter().addStyleName(row, "FlexTable-OddRow");
				else
					sectionTable.getRowFormatter().addStyleName(row, "FlexTable-EvenRow");
				row++;
			}
		}
		else
		{
			sectionTable.setWidget(0, 0, html);
		}
	}
	
	// Need this because getOffsetHeight doesn't return an accurate
	//	value until after the DOM has been updated. This will size
	//	the tab once it has been selected.
	@Override
	public void onSelection(SelectionEvent<Integer> event) {
		//TODO: get rid of hard-coded value here
		if (event.getSelectedItem() == Main.TAB_INDEX_SECTIONS) {
			//resize();		
		}
	}

	@Override
	public void onClick(ClickEvent event) {
		// TODO Auto-generated method stub
		Anchor a = (Anchor) event.getSource();
		int index = Integer.parseInt(a.getName());
		CodeSection s = this.sections.get(index);
		PlatformDescriptor pd = this.mpb.getPlatform();
		pd.section = s.name;
		pd.baseAddress = s.vma;
		this.mpb.setPlatform(pd);
		this.rent.selectTab(Main.TAB_INDEX_DISASSEMBLY);
	}
}
