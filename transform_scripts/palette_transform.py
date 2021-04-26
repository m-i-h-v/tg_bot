from PIL import Image
from colorsys import rgb_to_hls

def palette_transformation(filename, pl_num):
    palette = Image.open(f'palettes/palette_{pl_num}.jpg')
    x, y = palette.size
    colors_n = []
    b_w_hsl = []
    palette_pixels = palette.load()
    for i in range(x):
        colors_n.append([*palette_pixels[i, 0]] + [sum(palette_pixels[i, 0])])
        try:
            b_w_hsl.append(rgb_to_hls(palette_pixels[i, 0][0],
                                      palette_pixels[i, 0][1],
                                      palette_pixels[i, 0][2])[1])
        except ZeroDivisionError:
            b_w_hsl.append(0)
    image = Image.open(filename)
    x, y = image.size
    pixels = image.load()
    for i in range(x):
        for i_ in range(y):
            r, g, b = pixels[i, i_]
            c_sum = r + g + b
            b_w = 0.2989 * r + 0.587 * g + 0.114 * b
            try:
                hsl = rgb_to_hls(b_w, b_w, b_w)[1]
            except ZeroDivisionError:
                hsl = 0
            num = 200
            for color in range(len(colors_n)):
                local_sum = abs(c_sum - colors_n[color][-1])
                if local_sum < 25 and local_sum < num:
                    num = local_sum
                    n_color = colors_n[color][:3]
            if num == 200:
                for color in range(len(b_w_hsl)):
                    local_sum = abs(hsl - b_w_hsl[color])
                    if local_sum < num:
                        num = local_sum
                        n_color = colors_n[color][:3]
            pixels[i, i_] = tuple(n_color)
    image.save(filename)