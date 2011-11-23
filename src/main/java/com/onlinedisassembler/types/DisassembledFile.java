package com.onlinedisassembler.types;

import java.util.Date;
import java.util.Set;

import javax.persistence.Entity;
import javax.persistence.Table;

@Entity
@Table(name="disassembled_file")
public class DisassembledFile {
	Date dateUploaded;
	String filePath; 	
	String user;
	Set<Label> labels; 
	
}
