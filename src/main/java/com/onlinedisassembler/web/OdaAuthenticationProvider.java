package com.onlinedisassembler.web;

import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;

import com.google.common.collect.ImmutableList;

public class OdaAuthenticationProvider implements AuthenticationProvider {

	public Authentication authenticate(Authentication authentication)
			throws AuthenticationException {

		throw new AuthenticationException(authentication.getName()) {
		};
	}

	public boolean supports(Class<? extends Object> authentication) {
		return ImmutableList.of(UsernamePasswordAuthenticationToken.class)
				.contains(authentication);

	}
}
