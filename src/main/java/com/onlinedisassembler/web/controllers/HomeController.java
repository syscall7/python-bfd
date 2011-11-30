package com.onlinedisassembler.web.controllers;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

import com.onlinedisassembler.repository.Repository;
import com.onlinedisassembler.types.DisassembledFile;

@Controller
public class HomeController {
	
	@RequestMapping("/")
	public ModelAndView index() { 
		ModelAndView mav = new ModelAndView(); 		
		mav.setViewName("index");
		
		DisassembledFile file = new DisassembledFile();
		file.setUser("davis"); 
		file = new Repository<DisassembledFile, String>(DisassembledFile.class).save(file); 
		file = new Repository<DisassembledFile, String>(DisassembledFile.class).get(file.getId()); 
		return mav; 
	}
}
