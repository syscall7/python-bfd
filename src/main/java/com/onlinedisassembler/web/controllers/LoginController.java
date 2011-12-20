package com.onlinedisassembler.web.controllers;

import java.util.ArrayList;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.User;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

@Controller
public class LoginController {
	@Autowired
	@Qualifier("authenticationManager")
	protected AuthenticationManager authenticationManager;

	@ModelAttribute("user")
	public User formBackingObject(String username, String password) {
		return new User(username, password, true, true, true, true,
				new ArrayList<GrantedAuthority>());
	}

	@RequestMapping("/login")
	public String login(@ModelAttribute("user") User user) {
		UsernamePasswordAuthenticationToken token = new UsernamePasswordAuthenticationToken(
				user.getUsername(), user.getPassword());
		Authentication auth = authenticationManager.authenticate(token);
		SecurityContextHolder.getContext().setAuthentication(auth);
		ModelAndView mav = new ModelAndView();
		
		return "redirect:/"; 
		
	}
}
