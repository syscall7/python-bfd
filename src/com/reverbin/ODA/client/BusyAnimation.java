package com.reverbin.ODA.client;

import com.google.gwt.animation.client.Animation;
import com.google.gwt.user.client.ui.Image;

public class BusyAnimation extends Animation {

	private int count = 0;
	private int imageIndex = 0;
	private Image[] images;
	
	public BusyAnimation(Image[] imgs)
	{
		images = imgs;
		for (Image img : images)
		{
			img.setVisible(false);
		}
		images[0].setVisible(true);
	}
	
	private void nextImage()
	{
		if (images != null)
		{
			images[imageIndex].setVisible(false);
			imageIndex = imageIndex == images.length - 1 ? 0 : imageIndex + 1;
			images[imageIndex].setVisible(true);
		}
	}
	
	@Override
	protected void onUpdate(double progress) {
		if (0 == (count % 2))
		{
			nextImage();
		}
		count++;

	}
	
	@Override
	protected void onComplete() {
		if (images != null)
		{
			images[imageIndex].setVisible(false);
			images[0].setVisible(true);
		}
		imageIndex = 0;
		count = 0;

	}

}
