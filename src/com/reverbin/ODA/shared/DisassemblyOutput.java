package com.reverbin.ODA.shared;

import java.io.Serializable;

@SuppressWarnings("serial")
public class DisassemblyOutput implements Serializable {
	
	public DisassemblyOutput() {
		this.setFormattedAssembly("");
	}
	
	public DisassemblyOutput(String assembly) {
		this.setFormattedAssembly(assembly);
	}

	public void setFormattedAssembly(String formattedAssembly) {
		this.formattedAssembly = formattedAssembly;
	}

	public String getFormattedAssembly() {
		return formattedAssembly;
	}
	
	public void setTotalLines(int l) {
		totalLines = l;
	}
	
	public int getTotalLines() {
		return totalLines;
	}
	
	public void setCurrentLines(int l) {
		currentLines = l;
	}
	
	public int getCurrentLines() {
		return currentLines;
	}

	private int totalLines;
	private int currentLines;
	private String formattedAssembly;
}
