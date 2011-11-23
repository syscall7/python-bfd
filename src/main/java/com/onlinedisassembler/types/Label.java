package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="label")
public class Label {
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	
	String labelName; 
	Long offset;
	boolean isPublic;
	
	@ManyToOne
	DisassembledFile file; 
}
