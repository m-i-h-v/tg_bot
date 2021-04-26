import pygame
from PIL import Image
from colorsys import rgb_to_hls


pygame.init()
screen = pygame.display.set_mode((1600, 1200))
image = Image.open('transform_scripts/batb.jpg')
pixels = image.load()
palette = Image.open('palettes/palette_2.jpg')
palette_pixels = palette.load()
colors = []
colors_ = []
for i in range(12):
    colors.append(palette_pixels[i, 0])
for i in colors:
    c = i[0] * 0.2989 + i[1] * 0.587 + i[2] * 0.144
    colors_.append((c, c, c))

x, y = image.size
for i in range(x):
    for j in range(y):
        r_, g_, b_ = pixels[i, j]
        color_ = (r_, g_, b_)
        num_ = 123123123
        for color in colors:
            num = abs(r_ - color[0] + g_ - color[1] + b_ - color[2])
            if num < 25 and num < num_:
                num_ = num
                color_ = color
        if num_ == 123123123:
            if r_ + g_ + b_ <= 3:
                r_ += 1
                g_ += 1
                b_ += 1
            c = 0.2989 * r_ + 0.587 * g_ + 0.114 * b_
            hsl = rgb_to_hls(c, c, c)[1]
            color_ = (r_, g_, b_)
            num = 123123123
            for color in colors_:
                r, g, b = color
                if r + g + b <= 3:
                    r += 1
                    g += 1
                    b += 1
                color_hsl = rgb_to_hls(r, g, b)[1]
                if abs(hsl - color_hsl) < num:
                    num = color_hsl
                    color_ = color
            pygame.draw.line(screen, pygame.Color(colors[colors_.index(color_)]), (i, j), (i, j))
        else:
            pygame.draw.line(screen, pygame.Color(color_), (i, j), (i, j))


pygame.display.flip()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
    pygame.display.flip()