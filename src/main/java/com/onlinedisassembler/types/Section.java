package com.onlinedisassembler.types;

import java.util.Set;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="section")
public class Section {
	
	String id;
	
	DisassembledFile file; 
	
	String description; // user supplied description
	String sectionName;
	Long fileOffset; // start address in the file
	Long memoryOffset; // start address in memory
	Long size;
	Integer alignment;
	
	Set<String> sectionAttributes; // READ-ONLY, ALLOCATED

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

	public String getSectionName() {
		return sectionName;
	}

	public void setSectionName(String sectionName) {
		this.sectionName = sectionName;
	}

	public Long getFileOffset() {
		return fileOffset;
	}

	public void setFileOffset(Long fileOffset) {
		this.fileOffset = fileOffset;
	}

	public Long getMemoryOffset() {
		return memoryOffset;
	}

	public void setMemoryOffset(Long memoryOffset) {
		this.memoryOffset = memoryOffset;
	}

	public Long getSize() {
		return size;
	}

	public void setSize(Long size) {
		this.size = size;
	}

	public Integer getAlignment() {
		return alignment;
	}

	public void setAlignment(Integer alignment) {
		this.alignment = alignment;
	}

	public Set<String> getSectionAttributes() {
		return sectionAttributes;
	}

	public void setSectionAttributes(Set<String> sectionAttributes) {
		this.sectionAttributes = sectionAttributes;
	}
}
