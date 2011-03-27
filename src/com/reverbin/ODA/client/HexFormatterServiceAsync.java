package com.reverbin.ODA.client;

import com.google.gwt.user.client.rpc.AsyncCallback;
import com.reverbin.ODA.shared.FormattedOutput;
import com.reverbin.ODA.shared.PlatformDescriptor;

/**
 * The async counterpart of <code>FormatterService</code>.
 */
public interface HexFormatterServiceAsync {
	void formatHex(PlatformDescriptor platform, byte[] hex, AsyncCallback<FormattedOutput> callback)
			throws IllegalArgumentException;
}