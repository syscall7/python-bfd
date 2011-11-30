package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="functionarg")
public class FunctionArg {

	String id;
	DisassembledFile file; 

	String argName;
	String argType;
	String size;
	
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
	public String getArgName() {
		return argName;
	}
	public void setArgName(String argName) {
		this.argName = argName;
	}
	public String getArgType() {
		return argType;
	}
	public void setArgType(String argType) {
		this.argType = argType;
	}
	public String getSize() {
		return size;
	}
	public void setSize(String size) {
		this.size = size;
	}
	
}
