package com.onlinedisassembler.web.controllers;

import java.util.List;

import javax.servlet.RequestDispatcher;
import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.QueryParam;

import org.openid4java.OpenIDException;
import org.openid4java.consumer.ConsumerManager;
import org.openid4java.consumer.VerificationResult;
import org.openid4java.discovery.DiscoveryInformation;
import org.openid4java.discovery.Identifier;
import org.openid4java.message.AuthRequest;
import org.openid4java.message.AuthSuccess;
import org.openid4java.message.ParameterList;
import org.openid4java.message.ax.AxMessage;
import org.openid4java.message.ax.FetchRequest;
import org.openid4java.message.ax.FetchResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import com.onlinedisassembler.repository.UserRepository;
import com.onlinedisassembler.types.User;
import com.onlinedisassembler.web.OpenIDAuthenticationToken;

@Controller
public class OpenIDController {
	public ConsumerManager manager;

	@Autowired
	@Qualifier("authenticationManager")
	protected AuthenticationManager authenticationManager;

	public OpenIDController() {
		// instantiate a ConsumerManager object
		manager = new ConsumerManager();
	}

	public static final String GOOGLE_ENDPOINT = "https://www.google.com/accounts/o8/id";
	public static final String YAHOO_ENDPOINT = "https://me.yahoo.com";

	@RequestMapping("/openid")
	public String openId(HttpServletRequest request,
			@QueryParam("provider") String provider) {
		try {
			String userSuppliedString;
			if (provider.equals("google")) {
				userSuppliedString = GOOGLE_ENDPOINT;
			} else if (provider.equals("yahoo")) {
				userSuppliedString = YAHOO_ENDPOINT;
			} else {
				throw new RuntimeException(provider + " not recongnized");
			}

			// configure the return_to URL where your application will receive
			// the authentication responses from the OpenID provider
			String returnToUrl = "http://localhost:8082/openidVerify";

			// --- Forward proxy setup (only if needed) ---
			// ProxyProperties proxyProps = new ProxyProperties();
			// proxyProps.setProxyName("proxy.example.com");
			// proxyProps.setProxyPort(8080);
			// HttpClientFactory.setProxyProperties(proxyProps);

			// perform discovery on the user-supplied identifier
			List discoveries = manager.discover(userSuppliedString);

			// attempt to associate with the OpenID provider
			// and retrieve one service endpoint for authentication
			DiscoveryInformation discovered = manager.associate(discoveries);

			// store the discovery information in the user's session
			request.getSession().setAttribute("openid-disc", discovered);

			// obtain a AuthRequest message to be sent to the OpenID provider
			AuthRequest authReq = manager.authenticate(discovered, returnToUrl);

			// Attribute Exchange example: fetching the 'email' attribute
			FetchRequest fetch = FetchRequest.createFetchRequest();
			fetch.addAttribute("email",
			// attribute alias
					"http://schema.openid.net/contact/email", // type URI
					true); // required

			// attach the extension to the authentication request
			authReq.addExtension(fetch);

			if (true/* !discovered.isVersion2() */) {
				// Option 1: GET HTTP-redirect to the OpenID Provider endpoint
				// The only method supported in OpenID 1.x
				// redirect-URL usually limited ~2048 bytes
				return "redirect:" + authReq.getDestinationUrl(true);
				// httpResp.sendRedirect(authReq.getDestinationUrl(true));
				// return null;
			} else {
				// Option 2: HTML FORM Redirection (Allows payloads >2048 bytes)

				/*
				 * RequestDispatcher dispatcher = getServletContext()
				 * .getRequestDispatcher("formredirection.jsp");
				 * httpReq.setAttribute("parameterMap",
				 * authReq.getParameterMap());
				 * httpReq.setAttribute("destinationUrl",
				 * authReq.getDestinationUrl(false));
				 * dispatcher.forward(httpReq, httpResp);
				 */
			}
		} catch (OpenIDException e) {
			// present error to the user
		}

		return null;
	}

	@RequestMapping("/openidVerify")
	public String openidVerify(HttpServletRequest request) {
		try {
			// extract the parameters from the authentication response
			// (which comes in as a HTTP request from the OpenID provider)
			ParameterList response = new ParameterList(
					request.getParameterMap());

			// retrieve the previously stored discovery information
			DiscoveryInformation discovered = (DiscoveryInformation) request
					.getSession().getAttribute("openid-disc");

			// extract the receiving URL from the HTTP request
			StringBuffer receivingURL = request.getRequestURL();
			String queryString = request.getQueryString();
			if (queryString != null && queryString.length() > 0)
				receivingURL.append("?").append(request.getQueryString());

			// verify the response; ConsumerManager needs to be the same
			// (static) instance used to place the authentication request
			VerificationResult verification = manager.verify(
					receivingURL.toString(), response, discovered);

			// examine the verification result and extract the verified
			// identifier
			Identifier verified = verification.getVerifiedId();
			if (verified != null) {
				AuthSuccess authSuccess = (AuthSuccess) verification
						.getAuthResponse();

				if (authSuccess.hasExtension(AxMessage.OPENID_NS_AX)) {
					FetchResponse fetchResp = (FetchResponse) authSuccess
							.getExtension(AxMessage.OPENID_NS_AX);

					List emails = fetchResp.getAttributeValues("email");
					String email = (String) emails.get(0);

					User user = new UserRepository().createOrGetByEmail(email);

					Authentication token = new OpenIDAuthenticationToken(user);

					// Authentication auth =
					// authenticationManager.authenticate(token);
					SecurityContextHolder.getContext().setAuthentication(token);

					return "redirect:/";
				}
			}
		} catch (OpenIDException e) {
			// present error to the user
		}

		return null;

	}

}
