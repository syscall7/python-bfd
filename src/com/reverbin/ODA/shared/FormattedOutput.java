package com.reverbin.ODA.shared;

import java.io.Serializable;

@SuppressWarnings("serial")
public class FormattedOutput implements Serializable {
	public FormattedOutput() {
		this.setFormattedHex("");
		this.setFormattedAssembly("");
	}
	
	public FormattedOutput(String hex, String assembly, String s) {
		this.setFormattedHex(hex);
		this.setFormattedAssembly(assembly);
		this.setFormattedStrings(s);
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

	public String getFormattedStrings() {
		return strings;
	}

	public void setFormattedStrings(String s) {
		strings = s;
	}
	
	private String formattedHex;
	private String formattedAssembly;
	private String strings;
}
