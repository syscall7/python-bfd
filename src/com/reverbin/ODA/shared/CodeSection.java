package com.reverbin.ODA.shared;

import com.google.gwt.user.client.rpc.IsSerializable;


public class CodeSection implements IsSerializable {
	
	public CodeSection() {
		name = null;
		fileOffset = 0;
		vma = 0;
		lma = 0;
		alignment = 4;
		flags = null;
		index = 0;
		size = 0;
	}
	
	public String name;
	public Integer fileOffset; // start address in the file
	public Integer vma; // start address in memory
	public Integer lma;
	public Integer alignment;
	public String flags;
	public Integer index;
	public Integer size;
}
