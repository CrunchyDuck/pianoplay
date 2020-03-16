from PIL import Image, ImageDraw


class makeGreyStripes():
	def __init__(self):
		percentNotStriped = 0.38 # The amount of the texture that isn't striped.
		stripeWidth = 2 # width of the stripe in pixels. This is also the distance between each stripe.
		imageHeight = 500
		nonStriped = int(imageHeight * percentNotStriped)
		striped = imageHeight - nonStriped

		image = Image.new("RGB", (1, imageHeight))
		draw = ImageDraw.Draw(image)
		darkGrey = "#515151"
		lightGrey = "#737373"

		solidLine = [(0, 0), (0, imageHeight)]
		draw.line(solidLine, fill = darkGrey)

		for i in range(int(striped / 10)):
			gap = i * stripeWidth # The gap that should be left between each stripe to make the pattern.
			stripeStart = (i * 10) + nonStriped + gap # Where the start of the stripe is.
			stripeEnd = stripeStart + stripeWidth

			stripeLine = [(0, stripeStart), (0, stripeEnd)]
			draw.line(stripeLine, fill = lightGrey)



		image.save("GreyPanel.png")



makeGreyStripes()
