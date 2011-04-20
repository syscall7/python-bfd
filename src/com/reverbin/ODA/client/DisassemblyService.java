package com.reverbin.ODA.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.rpc.RemoteService;
import com.google.gwt.user.client.rpc.RemoteServiceRelativePath;
import com.reverbin.ODA.shared.*;

@RemoteServiceRelativePath("DisassemblyService")
public interface DisassemblyService extends RemoteService {

	/**
	 * Utility class for simplifying access to the instance of async service.
	 */
	public static class Util {
		private static DisassemblyServiceAsync instance;
		public static DisassemblyServiceAsync getInstance(){
			if (instance == null) {
				instance = GWT.create(DisassemblyService.class);
			}
			return instance;
		}
	}
	
	DisassemblyOutput disassemble(byte[] binary, PlatformDescriptor platformDesc) throws IllegalArgumentException;
	String strings(byte[] binary) throws IllegalArgumentException;
}
