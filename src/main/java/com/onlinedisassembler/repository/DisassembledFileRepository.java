package com.onlinedisassembler.repository;

import com.onlinedisassembler.types.DisassembledFile;

public class DisassembledFileRepository extends Repository<DisassembledFile, String>{

	public DisassembledFileRepository() {
		super(DisassembledFile.class);		
	}

}
