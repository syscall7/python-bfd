package com.reverbin.ODA.shared;

import java.io.Serializable;

@SuppressWarnings("serial")
public class DisassemblyOutput implements Serializable {
	
	public DisassemblyOutput() {
		this.setFormattedHex("");
		this.setFormattedAssembly("");
	}
	
	public DisassemblyOutput(String hex, String assembly, String s) {
		this.setFormattedHex(hex);
		this.setFormattedAssembly(assembly);
	}
		
		
	public void setFormattedHex(String formattedHex) {
		this.formattedHex = formattedHex;
	}

	public String getFormattedHex() {
		return formattedHex;
	}


	public void setFormattedAssembly(String formattedAssembly) {
		this.formattedAssembly = formattedAssembly;
	}

	public String getFormattedAssembly() {
		return formattedAssembly;
	}

	private String formattedHex;
	private String formattedAssembly;
}
