package com.onlinedisassembler.web.controllers;

import java.security.Principal;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.servlet.ModelAndView;

import com.onlinedisassembler.repository.DisassembledFileRepository;
import com.onlinedisassembler.repository.Repository;
import com.onlinedisassembler.types.DisassembledFile;
import com.onlinedisassembler.types.User;

@Controller
public class HomeController {

	@RequestMapping("/")
	public ModelAndView index() {
		ModelAndView mav = new ModelAndView();
		Authentication auth = SecurityContextHolder.getContext()
				.getAuthentication();
		mav.addObject("sessionId",
				RequestContextHolder
						.currentRequestAttributes().getSessionId());
		mav.addObject("loggedIn",
				!(auth instanceof AnonymousAuthenticationToken));
		if (!(auth instanceof AnonymousAuthenticationToken)) {
			User principal = (User) auth.getPrincipal();
			mav.addObject("username", principal.getUsername());
		}
		mav.setViewName("index");

		return mav;
	}
}
