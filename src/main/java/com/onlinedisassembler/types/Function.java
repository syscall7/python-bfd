package com.onlinedisassembler.types;

import java.util.Set;
import java.util.Map;


import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="function")
public class Function {
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	
	String functionName; 
	Long offset;  // Address in disassembly context
	Long fileOffset; // Offset into the raw file containing function bytes
	Integer length;  // size of the function
	
	// TODO: Need a representation for function arguments and their types
	Map<Integer, FunctionArg> functionArgs;
	String ReturnType; // argument returned by the function

	// TODO: Stack variable representation?
	
	String comment; // user generated comment describing the function
	Long signature; 

	boolean isPublic; // linkage type
	boolean isExported;
	
	
	@ManyToOne
	DisassembledFile file; 
}