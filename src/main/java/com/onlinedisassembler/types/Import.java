package com.onlinedisassembler.types;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="import")
public class Import {

	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	String id;
	String name;
	Long offset;
	String library;
}
