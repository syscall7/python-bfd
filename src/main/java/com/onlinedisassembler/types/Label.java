package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="label")
public class Label {
	
	String id;
	
	DisassembledFile file; 
	
	String labelName; 
	Long offset;
	boolean isPublic;
	
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
	public String getLabelName() {
		return labelName;
	}
	public void setLabelName(String labelName) {
		this.labelName = labelName;
	}
	public Long getOffset() {
		return offset;
	}
	public void setOffset(Long offset) {
		this.offset = offset;
	}
	public boolean isPublic() {
		return isPublic;
	}
	public void setPublic(boolean isPublic) {
		this.isPublic = isPublic;
	}
		
}
