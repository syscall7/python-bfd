package com.reverbin.ODA.client;

import com.google.gwt.user.client.ui.Image;

public class StatusIndicator {

	Image image;
	
	public StatusIndicator(Image img)
	{
		image = img;
	}
	
	public void setBusy(boolean busy)
	{
		if (image != null)
			image.setVisible(busy);
	}
}
