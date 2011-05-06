package com.reverbin.ODA.client;

import com.google.gwt.user.client.ui.HTML;

public class PayPalPanel extends HTML {

	public PayPalPanel()
	{
		this.setHTML(
				"<form action=\"https://www.paypal.com/cgi-bin/webscr\" method=\"post\">" +
				"<input type=\"hidden\" name=\"cmd\" value=\"_s-xclick\">" +
				"<input type=\"hidden\" name=\"hosted_button_id\" value=\"GJNASFRU457WN\">" +
				"<input type=\"image\" src=\"images/paypal-donate-button.gif\" border=\"0\" name=\"submit\" alt=\"PayPal - The safer, easier way to pay online!\">" +
				"<img alt=\"\" border=\"0\" src=\"https://www.paypalobjects.com/WEBSCR-640-20110401-1/en_US/i/scr/pixel.gif\" width=\"1\" height=\"1\">" + 
				"</form>");
	}
}
