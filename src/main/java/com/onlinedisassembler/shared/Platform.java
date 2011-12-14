package com.onlinedisassembler.shared;

import java.util.ArrayList;
import java.util.List;

public class Platform  {
	
	private static List<Platform> supportedPlatforms = new ArrayList<Platform>(){{
		add(new Platform(PlatformId.ARM, "arm", new Endian[] {Endian.LITTLE, Endian.BIG},new PlatformOption[] {PlatformOption.THUMB, PlatformOption.NONE}));
		add(new Platform(PlatformId.MIPS, "mips", new Endian[] {Endian.LITTLE, Endian.BIG},null));
		add(new Platform(PlatformId.PPC, "ppc", new Endian[] {Endian.LITTLE, Endian.BIG},null));
		add(new Platform(PlatformId.X86, "x86", new Endian[] {Endian.LITTLE},null));
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

	/**
	 * Supported disassembly options
	 */
	private List<PlatformOption> options = new ArrayList<PlatformOption>();
	
	
	public Platform(PlatformId pid, String n, Endian[] e, PlatformOption[] opts)
	{
		id = pid;
		name = n;
		endians.add(Endian.DEFAULT);
		for (Endian i : e)
			endians.add(i);
		if ( opts != null )
		{
			options.add(PlatformOption.DEFAULT);
			for (PlatformOption i : opts)
				options.add(i);
		}
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

	public List<PlatformOption> getOptions()
	{
		return options;
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
			if (p.name.equals(name)) {
				return p;
			}
		}
		return null;
	}
}
