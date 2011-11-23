package com.onlinedisassembler.web;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.webapp.WebAppContext;

public class WebServer {

	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception {
		Server server = new Server(8082);
		WebAppContext context = new WebAppContext();
		context.setResourceBase("src/main/webapp");		
		context.setDescriptor("WEB-INF/web.xml");		
		context.setContextPath("/");
		context.setParentLoaderPriority(true); 
		
		
		server.setHandler(context); 
		
		server.start(); 
		server.join(); 

	}

}
