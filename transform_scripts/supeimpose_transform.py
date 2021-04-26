from PIL import Image


def superimpose_transformation(filename, coef):
    image1 = Image.open(f'user_images/{filename}.jpg')
    image2 = Image.open(f'user_images/{filename}_.jpg')
    x1, y1 = image1.size
    x2, y2 = image2.size
    pixels1, pixels2 = image1.load(), image2.load()
    for i in range(x1):
        for i_ in range(y1):
            r1, g1, b1 = pixels1[i, i_]
            r2, g2, b2 = pixels2[i, i_]
            r = int(r1 * coef + r2 * (1 - coef))
            g = int(g1 * coef + g2 * (1 - coef))
            b = int(b1 * coef + b2 * (1 - coef))
            pixels1[i, i_] = r, g, b
    image1.save(f'user_images/{filename}.jpg')