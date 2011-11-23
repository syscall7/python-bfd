package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="datalabel")
public class DataLabel {
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	
	String variableName;  // name of this datavariable
	Long length;
	Long offset;
	Struct dataType; // contains information regarding the meaning of the bytes
	boolean isRaw; // whether or not dataLabel is a struct or just a simple int, byte
	
}
