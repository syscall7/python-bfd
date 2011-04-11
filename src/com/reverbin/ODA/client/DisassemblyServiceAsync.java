package com.reverbin.ODA.client;

import com.google.gwt.user.client.rpc.AsyncCallback;
import com.reverbin.ODA.shared.*;

/**
 * The async counterpart of <code>DisassemblyService</code>.
 */
public interface DisassemblyServiceAsync {
	void disassemble(byte[] binary, PlatformDescriptor platformDesc, AsyncCallback<DisassemblyOutput> callback) 
		throws IllegalArgumentException;
}