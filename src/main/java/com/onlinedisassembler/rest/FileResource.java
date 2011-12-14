package com.onlinedisassembler.rest;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Date;
import java.util.UUID;

import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.Consumes;
import javax.ws.rs.FormParam;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;

import com.onlinedisassembler.repository.Repository;
import com.onlinedisassembler.server.DisassemblyAnalyzer;
import com.onlinedisassembler.server.Objdump;
import com.onlinedisassembler.shared.Endian;
import com.onlinedisassembler.shared.ObjectType;
import com.onlinedisassembler.shared.PlatformDescriptor;
import com.onlinedisassembler.shared.PlatformId;
import com.onlinedisassembler.types.DisassembledFile;

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
	public String upload(@Context HttpServletRequest request,
			@FormDataParam("Filedata") InputStream file,
			@FormDataParam("Filedata") FormDataContentDisposition fileInfo) {

		int read = 0;
		byte[] bytes = new byte[1024];
		ObjectType objType = null;
		try {
			UUID fileId = UUID.randomUUID();
			File tmpFile = new File("/tmp/" + UUID.randomUUID());
			OutputStream out = new FileOutputStream(tmpFile);
			while ((read = file.read(bytes)) != -1) {
				if (objType == null) {
					if (bytes[0] == 'M' && bytes[1] == 'Z')
						objType = ObjectType.PE;
					else if (bytes[0] == 0x7f && bytes[1] == 'E'
							&& bytes[2] == 'L' && bytes[3] == 'F')
						objType = ObjectType.ELF;
					else {
						objType = ObjectType.BINARY;
					}
				}

				out.write(bytes, 0, read);
			}

			DisassembledFile dFile = new DisassembledFile();
			dFile.setDateUploaded(new Date());
			dFile.setRemoteAddr(request.getRemoteAddr());
			dFile.setOriginalFilename(fileInfo.getFileName());

			new Repository<DisassembledFile, String>(DisassembledFile.class)
					.save(dFile);

			PlatformDescriptor platformDesc = new PlatformDescriptor();
			platformDesc.baseAddress = 0;
			platformDesc.platformId = PlatformId.X86;
			platformDesc.endian = Endian.DEFAULT;

			String objDumpListing = Objdump.dis(platformDesc,
					tmpFile.getAbsolutePath(), objType);
			DisassemblyAnalyzer analyzer = new DisassemblyAnalyzer();
			analyzer.parseObjdumpListing(objDumpListing, 0, request.getContentLength(),
					platformDesc);
			String ret = analyzer.getDisassemblyOutput().getStringHtml();
			return ret; 

		} catch (IOException e) {
			throw new RuntimeException(e);
		}		
	}
}
