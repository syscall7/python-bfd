package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="functionarg")
public class FunctionArg {
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	String argName;
	String argType;
	String size;
	
}
