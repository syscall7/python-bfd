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
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;

import org.apache.commons.io.FileUtils;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

import com.google.gson.Gson;
import com.onlinedisassembler.repository.Repository;
import com.onlinedisassembler.server.DisassemblyAnalyzer;
import com.onlinedisassembler.server.Objdump;
import com.onlinedisassembler.shared.DisassemblyOutput;
import com.onlinedisassembler.shared.Endian;
import com.onlinedisassembler.shared.HexUtils;
import com.onlinedisassembler.shared.ObjectType;
import com.onlinedisassembler.shared.PlatformDescriptor;
import com.onlinedisassembler.shared.PlatformId;
import com.onlinedisassembler.types.DisassembledFile;
import com.onlinedisassembler.types.User;

import com.sun.jersey.core.header.FormDataContentDisposition;
import com.sun.jersey.multipart.FormDataParam;

@Path("/disassemble")
public class FileResource {
	final String HEXES = "0123456789ABCDEF";
	
	@POST
	@Produces(MediaType.TEXT_PLAIN)
	@Path("checkExisting")
	public String checkExisting(@FormParam("filename") String filename) {
		return "0";
	}

	@POST
	@Path("/uploadHex")
	@Consumes(MediaType.APPLICATION_FORM_URLENCODED)
	@Produces(MediaType.APPLICATION_JSON)
	public String uploadHex(@Context HttpServletRequest request,
			@FormParam("hex") String hex,
			@FormParam("platformId") PlatformId platformId,
			@FormParam("endian") Endian endian, 
			@FormParam("offset") String offset) throws IOException {
		byte [] bytes = HexUtils.textToBytes(hex);
		File tmpFile = new File("/tmp/hex/" + UUID.randomUUID());		
		FileUtils.writeByteArrayToFile(tmpFile, bytes);
		
		PlatformDescriptor platformDesc = new PlatformDescriptor();
		platformDesc.baseAddress = Integer.parseInt(offset.substring(2), 16); 
		platformDesc.platformId = platformId;
		platformDesc.endian = endian;
		
		ObjectType objType = null;
		int read = 0;
		FileInputStream file = FileUtils.openInputStream(tmpFile);
		final StringBuilder hexBuilder = new StringBuilder(2 * bytes.length);
		while ((read = file.read(bytes)) != -1) {
			if (objType == null) {
				objType = getObjectType(bytes); 
			}
			
			for (final byte b : bytes) {
				hexBuilder.append(HEXES.charAt((b & 0xF0) >> 4))
						.append(HEXES.charAt((b & 0x0F))).append(" ");
			}
		}

		
		DisassemblyOutput ret = disassemble(tmpFile, platformDesc, objType,
				hexBuilder);

		String returnJson = new Gson().toJson(ret);
		return returnJson;
	}
	
	private ObjectType getObjectType(byte [] bytes) { 
		ObjectType objType = null;
		if (bytes[0] == 'M' && bytes[1] == 'Z')
			objType = ObjectType.PE;
		else if (bytes[0] == 0x7f && bytes[1] == 'E'
				&& bytes[2] == 'L' && bytes[3] == 'F')
			objType = ObjectType.ELF;
		else {
			objType = ObjectType.BINARY;
		}
		return objType; 
	}

	private DisassemblyOutput disassemble(File tmpFile,
			PlatformDescriptor platformDesc, ObjectType objType,
			StringBuilder hexBuilder) {
		String objDumpListing = Objdump.dis(platformDesc,
				tmpFile.getAbsolutePath(), objType);
		DisassemblyAnalyzer analyzer = new DisassemblyAnalyzer();
		analyzer.parseObjdumpListing(objDumpListing, 0, 1000, platformDesc);
		DisassemblyOutput ret = analyzer.getDisassemblyOutput();
		ret.setHexDump(hexBuilder.toString());

		// Get String Data
		String strings = com.onlinedisassembler.server.Strings.strings(tmpFile
				.getAbsolutePath());
		ret.setStringHtml(strings);

		// Get Section Data for Elf files
		if (objType == ObjectType.ELF) {
			String sectionListing = Objdump.getSections(
					tmpFile.getAbsolutePath(), platformDesc);
			ret.setSectionHtml(analyzer.parseSectionData(sectionListing));
			ret.setSections(analyzer.getSections());
		} else {
			ret.setSectionHtml("<insn>No sections found</insn>");

		}
		return ret;

	}

	@POST
	@Path("/uploadFile")
	@Consumes(MediaType.MULTIPART_FORM_DATA)
	@Produces(MediaType.TEXT_PLAIN)
	public String upload(@Context HttpServletRequest request,
			@FormDataParam("Filedata") InputStream file,
			@FormDataParam("Filedata") FormDataContentDisposition fileInfo, 
			@FormDataParam("platformId") PlatformId platformId) {

		int read = 0;
		byte[] bytes = new byte[1024];
		ObjectType objType = null;
		try {
			UUID fileId = UUID.randomUUID();
			File tmpFile = new File("/tmp/" + UUID.randomUUID());
			OutputStream out = new FileOutputStream(tmpFile);			
			final StringBuilder hexBuilder = new StringBuilder(2 * bytes.length);

			while ((read = file.read(bytes)) != -1) {
				if (objType == null) {
					objType = getObjectType(bytes); 
				}

				out.write(bytes, 0, read);

				for (final byte b : bytes) {
					hexBuilder.append(HEXES.charAt((b & 0xF0) >> 4))
						.append(HEXES.charAt((b & 0x0F))).append(" ");
				}
			}
			out.close();

			DisassembledFile dFile = new DisassembledFile();
			dFile.setDateUploaded(new Date());
			dFile.setRemoteAddr(request.getRemoteAddr());
			dFile.setOriginalFilename(fileInfo.getFileName());
			dFile.setLength((long)bytes.length); 
			dFile.setArchitecture(platformId.toString()); 

			Authentication auth = SecurityContextHolder.getContext()
					.getAuthentication();
			if (!(auth instanceof AnonymousAuthenticationToken)) {
				User user = (User) auth.getPrincipal();
				dFile.setUser(user);
			}

			new Repository<DisassembledFile, String>(DisassembledFile.class)
					.save(dFile);

			PlatformDescriptor platformDesc = new PlatformDescriptor();
			platformDesc.baseAddress = 0;
			platformDesc.platformId = PlatformId.X86;
			platformDesc.endian = Endian.DEFAULT;

			DisassemblyOutput ret = disassemble(tmpFile, platformDesc, objType,
					hexBuilder);

			String returnJson = new Gson().toJson(ret);
			return returnJson;

		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}
}
