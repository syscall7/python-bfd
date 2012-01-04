package com.reverbin.ODA.shared;

import com.google.gwt.user.client.rpc.IsSerializable;

@SuppressWarnings("serial")
public class PlatformDescriptor  implements IsSerializable {

	public PlatformId platformId;
	public int baseAddress;
	public Endian endian;
	public PlatformOption option;
	public String section = "";
}
