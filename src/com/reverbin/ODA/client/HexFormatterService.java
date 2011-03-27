package com.reverbin.ODA.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.rpc.RemoteService;
import com.google.gwt.user.client.rpc.RemoteServiceRelativePath;
import com.reverbin.ODA.shared.*;


@RemoteServiceRelativePath("HexFormatterService")
public interface HexFormatterService extends RemoteService {
	/**
	 * Utility class for simplifying access to the instance of async service.
	 */
	public static class Util {
		private static HexFormatterServiceAsync instance;
		public static HexFormatterServiceAsync getInstance(){
			if (instance == null) {
				instance = GWT.create(HexFormatterService.class);
			}
			return instance;
		}
	}
	
	FormattedOutput formatHex(PlatformDescriptor platform, byte[] hex) throws IllegalArgumentException;
}