package com.reverbin.ODA.shared;

import java.io.Serializable;

@SuppressWarnings("serial")
public class FormattedOutput implements Serializable {
	public FormattedOutput() {
		this.setFormattedHex("");
		this.setFormattedAssembly("");
	}
	
	public FormattedOutput(String hex, String assembly) {
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
