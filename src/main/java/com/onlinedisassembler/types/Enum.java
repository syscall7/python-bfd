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

	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	String description; // User supplied description
	String EnumTypeName; // 
	Map<String, Integer> Members; // individual Enums and their field names
}
