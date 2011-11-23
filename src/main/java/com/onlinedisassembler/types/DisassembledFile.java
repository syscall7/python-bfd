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
	
	Date dateUploaded;
	String filePath; 	
	String user;
	
	@OneToMany
	Set<Label> labels; 
	
}
