package com.reverbin.ODA.client;

import com.reverbin.ODA.shared.PlatformDescriptor;

/**
 * Handles making the async calls to the server to update the disassembly based
 * on changes in the hex bytes or the platform selected.
 * 
 * @author anthony
 *
 */
public interface ViewUpdater {

	/**
	 * Update disassembly when hex bytes change
	 * @param hexBytes
	 */
	void updateHex(byte[] hexBytes);
	
	/**
	 * Update disassembly when platform changes
	 * 
	 * @param platform
	 */
	void updatePlatform(PlatformDescriptor platform);
}
