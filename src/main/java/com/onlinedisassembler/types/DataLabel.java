package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="datalabel")
public class DataLabel {

	String id;
	DisassembledFile file; 
	
	String variableName;  // name of this datavariable
	Long length;
	Long offset;
	Struct dataType; // contains information regarding the meaning of the bytes
	boolean isRaw; // whether or not dataLabel is a struct or just a simple int, byte
	
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public DisassembledFile getFile() {
		return file;
	}
	public void setFile(DisassembledFile file) {
		this.file = file;
	}
	public String getVariableName() {
		return variableName;
	}
	public void setVariableName(String variableName) {
		this.variableName = variableName;
	}
	public Long getLength() {
		return length;
	}
	public void setLength(Long length) {
		this.length = length;
	}
	public Long getOffset() {
		return offset;
	}
	public void setOffset(Long offset) {
		this.offset = offset;
	}
	public Struct getDataType() {
		return dataType;
	}
	public void setDataType(Struct dataType) {
		this.dataType = dataType;
	}
	public boolean isRaw() {
		return isRaw;
	}
	public void setRaw(boolean isRaw) {
		this.isRaw = isRaw;
	}

	
}
