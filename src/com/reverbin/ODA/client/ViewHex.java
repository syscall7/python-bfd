/**
 * 
 */
package com.reverbin.ODA.client;

import com.google.gwt.user.client.ui.*;

/**
 * Container for hex view
 * 
 * @author anthony
 *
 */
public class ViewHex {
	private String text;
	private byte[] bytes;
	ViewUpdater viewUpdater;
	TextArea hexArea;	

	/**
	 * Constructor
	 * @param asmView
	 */
	public ViewHex(ViewUpdater vu, TextArea area)
	{
		this.viewUpdater = vu;	// eventually we'll use this when the text area is edited
		this.hexArea = area;
	}
	
	/**
	 * Get the hex representation as ASCII text
	 * @return
	 */
	public String getText()
	{
		return this.text;
	}
	
	/**
	 * Set the hex representation as ASCII text
	 * @param t
	 */
	public void setText(String t)
	{
		this.text = t;
		this.hexArea.setText(t);
	}
	
	/**
	 * Get the hex representation as raw bytes
	 * @return
	 */
	public byte[] getRawBytes()
	{
		return this.bytes;
	}
	
	/**
	 * Set the hex representation as raw bytes
	 * @param b
	 */
	public void setRawBytes(byte[] b)
	{
		this.bytes = b;
	}
}
