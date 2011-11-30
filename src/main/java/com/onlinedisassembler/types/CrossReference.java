package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

// TODO: There's going to be a ton of these per disassembled file. 
//	Should we store them in the database or generate them at load-time???
@Entity
@Table(name="crossreference")
public class CrossReference {

	String id;
	
	DisassembledFile file; 
	

	Long offset; // WHere the xref occurs
	Long targetOffset; // address the address is targeting
	
	// Not sure if we need this
	Struct targetType; // What the xref is targeting (function, variable, etc)
	
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

	public Long getOffset() {
		return offset;
	}

	public void setOffset(Long offset) {
		this.offset = offset;
	}

	public Long getTargetOffset() {
		return targetOffset;
	}

	public void setTargetOffset(Long targetOffset) {
		this.targetOffset = targetOffset;
	}

	public Struct getTargetType() {
		return targetType;
	}

	public void setTargetType(Struct targetType) {
		this.targetType = targetType;
	}
	
}
