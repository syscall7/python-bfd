package com.onlinedisassembler.types;

import java.util.Set;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="section")
public class Section {
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	
	String description; // user supplied description
	String sectionName;
	Long fileOffset; // start address in the file
	Long memoryOffset; // start address in memory
	Long size;
	Integer alignment;
	
	Set<String> sectionAttributes; // READ-ONLY, ALLOCATED
}
