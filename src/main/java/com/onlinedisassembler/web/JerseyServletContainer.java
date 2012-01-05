package com.onlinedisassembler.web;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.onlinedisassembler.repository.OdaSessionFactory;
import com.sun.jersey.spi.container.servlet.ServletContainer;

public class JerseyServletContainer extends ServletContainer {
	@Override
	public void service(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		OdaSessionFactory.getSessionFactory().getCurrentSession()
				.beginTransaction();
		super.service(request, response);
		OdaSessionFactory.getSessionFactory().getCurrentSession()
				.getTransaction().commit();
	}
}
