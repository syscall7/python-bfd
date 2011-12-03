package com.onlinedisassembler.web;

import org.springframework.web.servlet.view.InternalResourceView;
import org.springframework.core.io.Resource;
import org.stringtemplate.v4.STGroup;
import org.stringtemplate.v4.ST;
import org.stringtemplate.v4.STGroupDir;
import org.stringtemplate.v4.STGroupFile;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.Map;
import java.io.PrintWriter;

public class StringTemplateView extends InternalResourceView {

	@Override
	protected void renderMergedOutputModel(Map model,
			HttpServletRequest request, HttpServletResponse response)
			throws Exception {

		Resource templateFile = getApplicationContext().getResource(getUrl());		
		ST template = new STGroupFile(templateFile.getFile().getPath(),'$','$')
				.getInstanceOf(getBeanName());
		// STGroup group = new
		// STGroupDir(templateFile.getFile().getParent(),'$','$');
		// ST template = group.getInstanceOf(getBeanName());
		/*for (Object e : model.keySet()) {
			template.add(e.toString(), model.get(e));
		}*/
		template.add("model", model);

		PrintWriter writer = response.getWriter();
		writer.print(template.render());
		writer.flush();
		writer.close();
	}
}
