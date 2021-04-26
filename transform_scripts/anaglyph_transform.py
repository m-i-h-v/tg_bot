from PIL import Image


def anaglyph_transformation(filename, delta):
    image = Image.open(f'user_images/{filename}.jpg')
    x, y = image.size
    pixels = image.load()
    res = Image.new('RGB', (x, y), (0, 0, 0))
    pixels_r = res.load()
    for i in range(x):
        for i_ in range(y):
            if i < delta:
                r, g, b = pixels[i, i_]
                pixels_r[i, i_] = 0, g, b
            else:
                pixels_r[i, i_] = r, g, b
                g, b = pixels[i, i_][1:]
                r = pixels[i - delta, i_][0]
    res.save(f'user_images/{filename}.jpg')
