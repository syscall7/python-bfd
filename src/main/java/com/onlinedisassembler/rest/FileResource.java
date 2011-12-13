package com.onlinedisassembler.rest;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import javax.ws.rs.Consumes;
import javax.ws.rs.FormParam;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

import com.sun.jersey.core.header.FormDataContentDisposition;
import com.sun.jersey.multipart.FormDataParam;

@Path("/disassembledfile")
public class FileResource {
	@POST
	@Produces(MediaType.TEXT_PLAIN)
	@Path("checkExisting")
	public String checkExisting(@FormParam("filename") String filename) {
		return "0";
	}

	@POST
	@Path("/upload")
	@Consumes(MediaType.MULTIPART_FORM_DATA)
	@Produces(MediaType.TEXT_PLAIN)
	public String upload(@FormDataParam("Filedata") InputStream file,
			@FormDataParam("Filedata") FormDataContentDisposition fileInfo) {
		
		int read = 0;		
		byte[] bytes = new byte[1024];
		
		
		try {
			OutputStream out = new FileOutputStream(new File("/tmp/" + fileInfo.getFileName()));
			while ((read = file.read(bytes)) != -1) {
				out.write(bytes, 0, read);
			}
		} catch (IOException e) {
			throw new RuntimeException(e); 
		}
		return "0";
	}
}
