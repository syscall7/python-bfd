package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="comment")
public class Comment {
	
	String id;

	DisassembledFile file; 
	
	String commentText; // User added comment text
	Long offset;  // Where in the disassembly the comment occurs
	
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
	public String getCommentText() {
		return commentText;
	}
	public void setCommentText(String commentText) {
		this.commentText = commentText;
	}
	public Long getOffset() {
		return offset;
	}
	public void setOffset(Long offset) {
		this.offset = offset;
	}
	
}
