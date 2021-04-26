from PIL import Image


def invert_transformation(filename):
    image = Image.open(f'user_images/{filename}.jpg')
    x, y = image.size
    pixels = image.load()
    for i in range(x):
        for i_ in range(y):
            r, g, b = pixels[i, i_]
            pixels[i, i_] = (255 - r, 255 - g, 255 - b)
    image.save(f'user_images/{filename}.jpg')