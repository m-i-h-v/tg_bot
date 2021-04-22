from PIL import Image
from colorsys import rgb_to_hls


def color_transformation(filename):
    image = Image.open(filename)
    x, y = image.size
    pixels = image.load()
    for x_ in range(x):
        for y_ in range(y):
            r, g, b = pixels[x_, y_]
            b_w = int(r * 0.2989 + g * 0.587 + b * 0.144)
            pixels[x_, y_] = (b_w, b_w, b_w)
    image.save(filename)