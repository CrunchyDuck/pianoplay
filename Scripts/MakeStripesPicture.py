from PIL import Image, ImageDraw
import random

"""Simple script that creates a series of varying brightness pixels in a vertical line. This is used for a material used by the piano."""
image = Image.new("RGB", (1, 100))
draw = ImageDraw.Draw(image)

for i in range(101):

	ran = random.randint(200, 255) # Darker colours make the surface more reflective.
	col = (ran, ran, ran)
	draw.point((0, i), fill = col)

image.save("Stripes.png")