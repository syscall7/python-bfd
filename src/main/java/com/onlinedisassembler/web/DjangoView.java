package com.onlinedisassembler.web;

import java.io.PrintWriter;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import net.asfun.jangod.template.TemplateEngine;

import org.springframework.core.io.Resource;
import org.springframework.web.servlet.view.InternalResourceView;

public class DjangoView extends InternalResourceView {

	/*final static TemplateEngine engine; // (2)
	static {
		engine = new TemplateEngine(); // (3)
		engine.getConfiguration().setWorkspace("D:/templates/"); // (1)
	}*/

	@Override
	protected void renderMergedOutputModel(Map model,
			HttpServletRequest request, HttpServletResponse response)
			throws Exception {
		TemplateEngine engine = new TemplateEngine(); 
		Resource templateFile = getApplicationContext().getResource(getUrl());
		String templatePath = templateFile.getFile().getPath();
		PrintWriter writer = response.getWriter();
		
		writer.print(engine.process(templatePath, model));
		writer.flush();
		writer.close();
	}
}
