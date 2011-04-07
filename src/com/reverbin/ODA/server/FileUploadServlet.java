package com.reverbin.ODA.server;

import java.io.File;
import java.io.IOException;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.FileItemFactory;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;
import org.apache.commons.io.FilenameUtils;

@SuppressWarnings("serial")
public class FileUploadServlet extends HttpServlet {

    private static final String UPLOAD_DIRECTORY = "c:\\upload\\";

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        super.doGet(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        
        // process only multipart requests
        if (ServletFileUpload.isMultipartContent(req)) {

            // Create a factory for disk-based file items
            FileItemFactory factory = new DiskFileItemFactory();

            // Create a new file upload handler
            ServletFileUpload upload = new ServletFileUpload(factory);

            // Parse the request
            try {
                List<FileItem> items = upload.parseRequest(req);
                for (FileItem item : items) {
                    // process only file upload - discard other form item types
                    if (item.isFormField()) continue;
                    
                    String fileName = item.getName();
                    // get only the file name not whole path
                    if (fileName != null) {
                        fileName = FilenameUtils.getName(fileName);
                    }

                    byte[] hex = item.get();
                    final String HEXES = "0123456789ABCDEF";
            		StringBuilder builder = new StringBuilder(2 * hex.length);

            		for ( final byte b : hex ) {
            	    	builder.append(HEXES.charAt((b & 0xF0) >> 4))
            	         .append(HEXES.charAt((b & 0x0F)))
            	         .append(" ");
            	    }
            		
            		// prevent client browser from adding <pre> tags to the response
            		resp.setContentType("text/html");
                    resp.setStatus(HttpServletResponse.SC_CREATED);
                    resp.getWriter().print(builder.toString());
                    resp.flushBuffer();
                    
                }
            } catch (Exception e) {
                resp.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
                        "An error occurred while creating the file : " + e.getMessage());
            }

        } else {
            resp.sendError(HttpServletResponse.SC_UNSUPPORTED_MEDIA_TYPE,
                            "Request contents type is not supported by the servlet.");
        }
    }
}