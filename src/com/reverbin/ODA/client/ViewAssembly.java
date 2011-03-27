package com.reverbin.ODA.client;

import com.google.gwt.user.client.ui.*;
import com.reverbin.ODA.shared.PlatformDescriptor;
import com.google.gwt.event.dom.client.*;

/**
 * Container for assembly view
 * 
 * @author anthony
 *
 */
public class ViewAssembly implements ChangeHandler {
	
	HTML display;
	PlatformDescriptor platform = new PlatformDescriptor("x86");
	ViewUpdater viewUpdater;
	
	/**
	 * Constructor
	 * 
	 * @param vu
	 * @param d
	 */
	public ViewAssembly(ViewUpdater vu, HTML d)
	{
		this.display = d;
		this.viewUpdater = vu;
	}
	
	/**
	 * Handle platform selection
	 */
	public void onChange(ChangeEvent event) 
	{
		ListBox box = (ListBox)event.getSource();
		String p = box.getItemText(box.getSelectedIndex());
		this.setPlatform(new PlatformDescriptor(p));
		this.viewUpdater.updatePlatform(this.getPlatform());
    }
	
	/**
	 * Set the formatted assembly
	 * 
	 * @param assembly
	 */
	public void setText(String assembly)
	{
		this.display.setHTML(assembly);
	}
	
	/**
	 * Get the formatted assembly
	 * @return
	 */
	public String getText()
	{
		return this.display.getText();
	}
	
	/**
	 * Set the platform for which to disassemble
	 * @param p
	 */
	public void setPlatform(PlatformDescriptor p)
	{
		this.platform = p;
	}
	
	/**
	 * Get the platform for which to disassemble
	 * @return
	 */
	public PlatformDescriptor getPlatform()
	{
		return this.platform;
	}
}
