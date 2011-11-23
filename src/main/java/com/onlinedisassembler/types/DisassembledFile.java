package com.onlinedisassembler.types;

import java.util.Date;
import java.util.Set;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.OneToMany;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="disassembled_file")
public class DisassembledFile {
	
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	String fileType; // binary, elf, PE, Hex, etc.
	
	Date dateUploaded;
	String filePath; 	
	String user;
	String userGroup;
	String version; // ability to track multiple versions of disassembled files

	String architecture;
	String processor;
	String compiler;

	String description; // User-supplied description
	
	Long loadOffset; // Maybe just a portion of the file is loaded for disassembly
	Long length; // size of the disassembled portion of the file
	
	String signature; // MD5 maybe?  If multiple users are disassembling the same file
						// we could detect it and leverage existing data
	
	@OneToMany
	Set<Label> labels; 
	
}
