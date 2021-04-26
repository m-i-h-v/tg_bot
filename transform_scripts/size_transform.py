from PIL import Image


def size_transformation(filename, save_ratio, width=None, height=None):
    image = Image.open(f'user_images/{filename}.jpg')
    x, y = image.size
    if width is None:
        width = x
    elif height is None:
        height = y
    if save_ratio:
        image.thumbnail((width, height), Image.ANTIALIAS)
    else:
        image = image.resize((width, height), Image.ANTIALIAS)
    image.save(f'user_images/{filename}.jpg')