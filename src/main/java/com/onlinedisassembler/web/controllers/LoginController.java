package com.onlinedisassembler.web.controllers;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

//@Controller
public class LoginController {
	
	@RequestMapping("/login")
	public ModelAndView login() { 
		ModelAndView mav = new ModelAndView(); 		
		mav.setViewName("login");
		return mav; 
	}
}
