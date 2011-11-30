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

	String id;
	
	DisassembledFile file; 
	
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
	
	@Id
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	
	@ManyToOne
	public DisassembledFile getFile() {
		return file;
	}
	public void setFile(DisassembledFile file) {
		this.file = file;
	}
	public String getFunctionName() {
		return functionName;
	}
	public void setFunctionName(String functionName) {
		this.functionName = functionName;
	}
	public Long getOffset() {
		return offset;
	}
	public void setOffset(Long offset) {
		this.offset = offset;
	}
	public Long getFileOffset() {
		return fileOffset;
	}
	public void setFileOffset(Long fileOffset) {
		this.fileOffset = fileOffset;
	}
	public Integer getLength() {
		return length;
	}
	public void setLength(Integer length) {
		this.length = length;
	}
	public Map<Integer, FunctionArg> getFunctionArgs() {
		return functionArgs;
	}
	public void setFunctionArgs(Map<Integer, FunctionArg> functionArgs) {
		this.functionArgs = functionArgs;
	}
	public String getReturnType() {
		return ReturnType;
	}
	public void setReturnType(String returnType) {
		ReturnType = returnType;
	}
	public String getComment() {
		return comment;
	}
	public void setComment(String comment) {
		this.comment = comment;
	}
	public Long getSignature() {
		return signature;
	}
	public void setSignature(Long signature) {
		this.signature = signature;
	}
	public boolean isPublic() {
		return isPublic;
	}
	public void setPublic(boolean isPublic) {
		this.isPublic = isPublic;
	}
	public boolean isExported() {
		return isExported;
	}
	public void setExported(boolean isExported) {
		this.isExported = isExported;
	}
	
	
	
}