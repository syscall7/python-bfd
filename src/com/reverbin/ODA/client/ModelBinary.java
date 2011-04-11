package com.reverbin.ODA.client;

import java.util.List;
import java.util.ArrayList;

/**
 * Contains the state of the binary we are disassembling
 * @author anthony
 *
 */
public class ModelBinary {

	/**
	 * Binary data we are currently disassembling
	 */
	private byte[] bytes = {};
	
	/**
	 * Views that need updating if our binary state changes
	 */
	private List<ModelBinaryListener> listeners = new ArrayList<ModelBinaryListener>();
	
	/**
	 * Notify observers that our state changed
	 */
	private void notifyObservers()
	{
		for (ModelBinaryListener mbl : listeners)
		{
			mbl.onBinaryChange(this);
		}
	}
	
	/**
	 * Add a new listener
	 * @param mbl
	 */
	public void addBinaryListner(ModelBinaryListener mbl)
	{
		listeners.add(mbl);
	}
	
	/**
	 * Update binary state
	 * @param b
	 */
	public void setBytes(byte[] b)
	{
		bytes = b;
		notifyObservers();
	}
	
	/**
	 * Get binary state
	 * @return
	 */
	public byte[] getBytes()
	{
		return bytes;
	}
	
}
