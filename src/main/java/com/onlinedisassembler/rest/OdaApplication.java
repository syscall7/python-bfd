package com.onlinedisassembler.rest;

import java.util.HashSet;
import java.util.Set;

import javax.ws.rs.core.Application;

public class OdaApplication extends Application {
	@Override
	public Set<Class<?>> getClasses() { 
		Set<Class<?>> s = new HashSet<Class<?>>(); 
		s.add(FileResource.class); 
		return s; 
	}
}
