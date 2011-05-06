package com.reverbin.ODA.client;

import java.util.ArrayList;
import java.util.List;

import com.reverbin.ODA.shared.Endian;
import com.reverbin.ODA.shared.PlatformDescriptor;
import com.reverbin.ODA.shared.PlatformId;

public class ModelPlatformBin {

	public int MODEL_EVENT_PLATFORM_CHANGED = 1 << 1;
	public int MODEL_EVENT_BIN_CHANGED  = 1 << 2;
	
	/**
	 * Binary data we are currently disassembling
	 */
	private byte[] bytes = {};
	
	/**
	 * Platform state
	 */
	private PlatformDescriptor platformDesc = new PlatformDescriptor();
	
	/**
	 * Views that need updating if our binary state changes
	 */
	private List<ModelPlatformBinListener> listeners = new ArrayList<ModelPlatformBinListener>();
	
	public ModelPlatformBin()
	{	
		// set default state
		platformDesc.baseAddress = 0;
		platformDesc.platformId = PlatformId.X86;
		platformDesc.endian = Endian.LITTLE;	
	}
	
	/**
	 * Notify observers that our state changed
	 */
	private void notifyObservers(int eventFlags)
	{
		for (ModelPlatformBinListener mabl : listeners)
		{
			mabl.onChange(this, eventFlags);
		}
	}
	
	/**
	 * Add a new listener
	 * @param mbl
	 */
	public void addListener(ModelPlatformBinListener mabl)
	{
		listeners.add(mabl);
	}
	
	/**
	 * Update binary state
	 * @param b
	 */
	public void setBytes(byte[] b)
	{
		bytes = b;
		notifyObservers(MODEL_EVENT_BIN_CHANGED);
	}
	
	/**
	 * Get binary state
	 * @return
	 */
	public byte[] getBytes()
	{
		return bytes;
	}
	
	/**
	 * Update platform state
	 * @param pd
	 */
	public void setPlatform(PlatformDescriptor pd)
	{
		platformDesc = pd;
		notifyObservers(MODEL_EVENT_PLATFORM_CHANGED);
	}
	
	/**
	 * Get platform state
	 * @return
	 */
	public PlatformDescriptor getPlatform()
	{
		return platformDesc;
	}
	
	public void setPlatformBin(PlatformDescriptor pd, byte[] b)
	{
		platformDesc = pd;
		bytes = b;
		notifyObservers(MODEL_EVENT_PLATFORM_CHANGED | MODEL_EVENT_BIN_CHANGED);
	}
}
