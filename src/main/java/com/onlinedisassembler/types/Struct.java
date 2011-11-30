package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="struct")
public class Struct {
	
	
	String id;
	
	DisassembledFile file; 

	String description; // User-supplied description
	String typeName; // Name of the user-defined type. Struct etc
	
	String memberRepresentation; // fields of the structure  
	
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
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public String getTypeName() {
		return typeName;
	}
	public void setTypeName(String typeName) {
		this.typeName = typeName;
	}
	public String getMemberRepresentation() {
		return memberRepresentation;
	}
	public void setMemberRepresentation(String memberRepresentation) {
		this.memberRepresentation = memberRepresentation;
	}
	
}
