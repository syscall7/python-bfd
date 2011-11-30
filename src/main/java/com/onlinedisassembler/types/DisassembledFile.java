package com.onlinedisassembler.types;

import java.util.Date;
import java.util.Set;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.ManyToOne;
import javax.persistence.OneToMany;
import javax.persistence.Table;

import org.hibernate.annotations.GenericGenerator;

@Entity
@Table(name="disassembled_file")
public class DisassembledFile {
		
	String id;
	String fileType; // binary, elf, PE, Hex, etc.
	
	Date dateUploaded;
	String filePath; 	
	String user;
	String userGroup;
	String version; // ability to track multiple versions of disassembled files

	String architecture;
	String processor;
	String compiler;

	String description; // User-supplied description
	
	Long loadOffset; // Maybe just a portion of the file is loaded for disassembly
	Long length; // size of the disassembled portion of the file
	
	String signature; // MD5 maybe?  If multiple users are disassembling the same file
						// we could detect it and leverage existing data
	
	@Id
	@GeneratedValue(generator = "uuid")
	@GenericGenerator(name = "uuid", strategy = "uuid2")
	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public String getFileType() {
		return fileType;
	}

	public void setFileType(String fileType) {
		this.fileType = fileType;
	}

	public Date getDateUploaded() {
		return dateUploaded;
	}

	public void setDateUploaded(Date dateUploaded) {
		this.dateUploaded = dateUploaded;
	}

	public String getFilePath() {
		return filePath;
	}

	public void setFilePath(String filePath) {
		this.filePath = filePath;
	}

	public String getUser() {
		return user;
	}

	public void setUser(String user) {
		this.user = user;
	}

	public String getUserGroup() {
		return userGroup;
	}

	public void setUserGroup(String userGroup) {
		this.userGroup = userGroup;
	}

	public String getVersion() {
		return version;
	}

	public void setVersion(String version) {
		this.version = version;
	}

	public String getArchitecture() {
		return architecture;
	}

	public void setArchitecture(String architecture) {
		this.architecture = architecture;
	}

	public String getProcessor() {
		return processor;
	}

	public void setProcessor(String processor) {
		this.processor = processor;
	}

	public String getCompiler() {
		return compiler;
	}

	public void setCompiler(String compiler) {
		this.compiler = compiler;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public Long getLoadOffset() {
		return loadOffset;
	}

	public void setLoadOffset(Long loadOffset) {
		this.loadOffset = loadOffset;
	}

	public Long getLength() {
		return length;
	}

	public void setLength(Long length) {
		this.length = length;
	}

	public String getSignature() {
		return signature;
	}

	public void setSignature(String signature) {
		this.signature = signature;
	}
	
}
