package com.reverbin.ODA.client;

import com.reverbin.ODA.shared.*;
import java.util.List;
import java.util.ArrayList;

public class ModelPlatform {

	/**
	 * Platform state
	 */
	private PlatformDescriptor platformDesc = new PlatformDescriptor();
	
	/**
	 * Views that need updating if our state changes
	 */
	private List<ModelPlatformListener> listeners = new ArrayList<ModelPlatformListener>();
	
	/**
	 * Supported platforms
	 * TODO: Get this by RPC
	 */
	private List<Platform> platforms = new ArrayList<Platform>();
	
	public ModelPlatform()
	{	
		// set default state
		platformDesc.baseAddress = 0;
		platformDesc.platformId = PlatformId.X86;
		platformDesc.endian = Endian.LITTLE;
		
	}
	
	/**
	 * Notify observers that our state changed
	 */
	private void notifyObservers()
	{
		for (ModelPlatformListener mpl : listeners)
		{
			mpl.onPlatformChange(this);
		}
	}
	
	/**
	 * Add a new listener
	 * @param mpl
	 */
	public void addPlatformListner(ModelPlatformListener mpl)
	{
		listeners.add(mpl);
	}
	
	/**
	 * Update platform state
	 * @param pd
	 */
	public void setPlatform(PlatformDescriptor pd)
	{
		platformDesc = pd;
		notifyObservers();
	}
	
	/**
	 * Get platform state
	 * @return
	 */
	public PlatformDescriptor getPlatform()
	{
		return platformDesc;
	}
	
}
