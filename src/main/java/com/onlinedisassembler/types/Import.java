package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="import")
public class Import {
	
	
	String id;
	DisassembledFile file; 

	String name;
	Long offset;
	String library;
	
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	
	@ManyToOne
	public DisassembledFile getFile() {
		return file;
	}
	public void setFile(DisassembledFile file) {
		this.file = file;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public Long getOffset() {
		return offset;
	}
	public void setOffset(Long offset) {
		this.offset = offset;
	}
	public String getLibrary() {
		return library;
	}
	public void setLibrary(String library) {
		this.library = library;
	}
	

}
