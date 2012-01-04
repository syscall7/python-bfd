package com.onlinedisassembler.repository;

import java.util.List;

import org.hibernate.Session;
import org.hibernate.criterion.Restrictions;

public class Repository<T, Tid> {

	Class<T> entityClass;
	Session session;

	public Repository(Class<T> entityClass) {
		this.entityClass = entityClass;
	}

	public synchronized Session getSession() {
		if (session == null) {
			session = OdaSessionFactory.getSessionFactory().getCurrentSession();
		}
		return session;
	}

	@SuppressWarnings("unchecked")
	public T get(Tid id) {
		T t = (T) getSession().createCriteria(entityClass)
				.add(Restrictions.idEq(id)).uniqueResult();
		return t;
	}

	public List<T> getAll(String fieldName, String fieldValue) {
		return (List<T>)getSession().createCriteria(entityClass)
				.add(Restrictions.eq(fieldName, fieldValue)).list();
	}

	public T save(T toSave) {
		getSession().save(toSave);
		getSession().flush();
		return toSave;
	}
}
