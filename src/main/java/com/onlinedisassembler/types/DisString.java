package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="dis_string")
public class DisString {

	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	
	String text;
	String type; // Unicode, Null terminated, etc
	Integer length;
	Long offset;
}
