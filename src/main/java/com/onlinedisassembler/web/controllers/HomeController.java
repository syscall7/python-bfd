package com.onlinedisassembler.web.controllers;

import java.security.Principal;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.servlet.ModelAndView;

import com.onlinedisassembler.repository.DisassembledFileRepository;
import com.onlinedisassembler.repository.Repository;
import com.onlinedisassembler.types.DisassembledFile;

@Controller
public class HomeController {

	@RequestMapping("/")
	public ModelAndView index() {
		ModelAndView mav = new ModelAndView();
		Authentication auth = SecurityContextHolder.getContext()
				.getAuthentication();
		mav.addObject("loggedIn", !(auth instanceof AnonymousAuthenticationToken));
		mav.addObject("username", auth.getPrincipal()); 
		mav.setViewName("index");

		DisassembledFile file = new DisassembledFile();

		file.setUser("davis");

		file = new DisassembledFileRepository().save(file);
		file = new DisassembledFileRepository().get(file.getId());
		return mav;
	}
}
