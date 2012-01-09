package com.onlinedisassembler.web;

import java.util.ArrayList;
import java.util.List;

import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;

import com.onlinedisassembler.types.User;

public class OpenIDAuthenticationToken extends AbstractAuthenticationToken {


	private User identity;
	private String message;

	public OpenIDAuthenticationToken(User identity) {
		super(new ArrayList<GrantedAuthority>());
		this.identity = identity;
		setAuthenticated(true);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.acegisecurity.Authentication#getPrincipal()
	 */
	public Object getPrincipal() {
		return identity;
	}

	@Override
	public Object getCredentials() {
		// TODO Auto-generated method stub
		return null;
	}

}
