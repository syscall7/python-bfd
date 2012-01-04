package com.onlinedisassembler.web;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.hibernate.classic.Session;
import org.springframework.web.servlet.handler.HandlerInterceptorAdapter;

import com.onlinedisassembler.repository.OdaSessionFactory;

public class HibernateSessionInterceptor extends HandlerInterceptorAdapter{
	
	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
		    throws Exception {
		Session session = OdaSessionFactory.getSessionFactory().getCurrentSession();
		session.beginTransaction(); 
		return true; 
	}
	
	@Override
	public void afterCompletion(
			HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex)
			throws Exception {
		Session session = OdaSessionFactory.getSessionFactory().getCurrentSession();
		session.getTransaction().commit(); 		
	}
}
