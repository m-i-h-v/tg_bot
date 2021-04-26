from PIL import Image


def anaglyph_transformation(filename, delta):
    image = Image.open(f'user_images/{filename}.jpg')
    x, y = image.size
    pixels = image.load()
    res = Image.new('RGB', (x, y), (0, 0, 0))
    pixels_r = res.load()
    for i in range(x):
        for j in range(y):
            if i < delta:
                r, g, b = pixels[i, j]
                pixels_r[i, j] = 0, g, b
            else:
                pixels_r[i, j] = r, g, b
                g, b = pixels[i, j][1:]
                r = pixels[i - delta, j][0]
    res.save(f'user_images/{filename}.jpg')