package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

// TODO: There's going to be a ton of these per disassembled file. 
//	Should we store them in the database or generate them at load-time???
@Entity
@Table(name="crossreference")
public class CrossReference {
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	
	Long offset; // WHere the xref occurs
	Long targetOffset; // address the address is targeting
	
	// Not sure if we need this
	Struct targetType; // What the xref is targeting (function, variable, etc)
	
}
