package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="comment")
public class Comment {
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	
	String commentText; // User added comment text
	Long offset;  // Where in the disassembly the comment occurs
	
}
