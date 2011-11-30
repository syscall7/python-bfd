package com.onlinedisassembler.types;

import java.util.Map;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;


// I could see these belonging to a disassembly file and I could also
//	see a general collection of universally applicable enums that users
//	could bring into the disassembly.  For example, a TCP_PORT enum with HTTP 80
//	etc..
@Entity
@Table(name="enum")
public class Enum {

	String id;
	DisassembledFile file; 
	String description; // User supplied description
	String EnumTypeName; // 
	Map<String, Integer> Members; // individual Enums and their field names
	
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
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public String getEnumTypeName() {
		return EnumTypeName;
	}
	public void setEnumTypeName(String enumTypeName) {
		EnumTypeName = enumTypeName;
	}
	public Map<String, Integer> getMembers() {
		return Members;
	}
	public void setMembers(Map<String, Integer> members) {
		Members = members;
	}
	
	
}
