package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="struct")
public class Struct {
	
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;

	String description; // User-supplied description
	String typeName; // Name of the user-defined type. Struct etc
	String memberRepresentation; // fields of the structure  
	
}
