package com.onlinedisassembler.web;

import java.util.ArrayList;

import org.springframework.dao.DataAccessException;
import org.springframework.security.authentication.encoding.ShaPasswordEncoder;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;

import com.onlinedisassembler.types.User;

public class OdaUserDetailsService implements UserDetailsService {

	public UserDetails loadUserByUsername(String username)
			throws UsernameNotFoundException, DataAccessException {
		; 
		return new User(username, new ShaPasswordEncoder().encodePassword("password", username)); 
		//throw new UsernameNotFoundException(username); 
	}

}
