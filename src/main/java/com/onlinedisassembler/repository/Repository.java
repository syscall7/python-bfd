package com.onlinedisassembler.repository;

import org.hibernate.Session;

public class Repository<T,Tid> {
	
	Class<T> entityClass; 
	Session session; 
	public Repository(Class<T> entityClass) { 
		this.entityClass = entityClass; 
	}
	
	private synchronized Session getSession() { 
		if (session==null) { 
			session = OdaSessionFactory.getSessionFactory().getCurrentSession();
		}
		return session; 
	}
	
	public T save(T toSave) {
		return toSave; 
	}
}
