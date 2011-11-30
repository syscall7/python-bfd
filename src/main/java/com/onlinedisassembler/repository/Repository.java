package com.onlinedisassembler.repository;

import org.hibernate.Session;
import org.hibernate.criterion.Restrictions;

public class Repository<T, Tid> {

	Class<T> entityClass;
	Session session;

	public Repository(Class<T> entityClass) {
		this.entityClass = entityClass;
	}

	private synchronized Session getSession() {
		if (session == null) {
			session = OdaSessionFactory.getSessionFactory().getCurrentSession();
		}
		return session;
	}

	@SuppressWarnings("unchecked")
	public T get(Tid id) {
		getSession().beginTransaction(); 
		T t = (T) getSession().createCriteria(entityClass)
				.add(Restrictions.idEq(id)).uniqueResult();
		getSession().getTransaction().commit(); 
		return t; 
	}

	public T save(T toSave) {
		getSession().beginTransaction();
		getSession().save(toSave);
		getSession().flush();
		getSession().getTransaction().commit();
		return toSave;
	}
}
