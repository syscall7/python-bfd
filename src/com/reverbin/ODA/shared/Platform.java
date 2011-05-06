package com.reverbin.ODA.shared;

import java.util.ArrayList;
import java.util.List;

import com.reverbin.ODA.client.ModelBinaryListener;

public class Platform  {
	
	private static List<Platform> supportedPlatforms = new ArrayList<Platform>(){{
		add(new Platform(PlatformId.ARM, "arm", new Endian[] {Endian.LITTLE, Endian.BIG}));
		add(new Platform(PlatformId.MIPS, "mips", new Endian[] {Endian.LITTLE, Endian.BIG}));
		add(new Platform(PlatformId.PPC, "ppc", new Endian[] {Endian.LITTLE, Endian.BIG}));
		add(new Platform(PlatformId.X86, "x86", new Endian[] {Endian.LITTLE}));
		//add(new Platform(PlatformId.TMS320C6X, "TI TMS320C6X", new Endian[] {Endian.LITTLE}));
		//add(new Platform(PlatformId.TMS320C80, "TI TMS320C80", new Endian[] {Endian.LITTLE}));
	}};
	
	/**
	 * Platform identifier
	 */
	private PlatformId id;
	
	/**
	 * Readable name
	 */
	private String name;
	
	/**
	 * Supported endianness
	 */
	private List<Endian> endians = new ArrayList<Endian>();
	
	public Platform(PlatformId pid, String n, Endian[] e)
	{
		id = pid;
		name = n;
		endians.add(Endian.DEFAULT);
		for (Endian i : e)
			endians.add(i);
	}
	
	public PlatformId getId()
	{
		return id;
	}
	
	public String getName()
	{
		return name;
	}
	
	public List<Endian> getEndians()
	{
		return endians;
	}
	
	/**
	 * Get all supported platforms
	 * @return
	 */
	public static List<Platform> getSupportedPlatforms()
	{
		return supportedPlatforms;
	}
	
	public static Platform getPlatform(PlatformId id)
	{
		for (Platform p : supportedPlatforms) {
			if (p.id == id) {
				return p;
			}
		}
		return null;
	}
	
	
	public static Platform getPlatform(String name)
	{
		for (Platform p : supportedPlatforms) {
			if (p.name == name) {
				return p;
			}
		}
		return null;
	}
}
