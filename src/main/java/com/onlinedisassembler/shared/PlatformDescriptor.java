package com.onlinedisassembler.shared;

@SuppressWarnings("serial")
public class PlatformDescriptor {

	public PlatformId platformId;
	public int baseAddress;
	public Endian endian;
	public PlatformOption option;
	public String section = "";
}
