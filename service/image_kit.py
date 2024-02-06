from os import listdir
from typing import Any, Tuple

from loguru import logger
from PIL import Image, ImageDraw, ImageFont
from util.typing_util import BinFunc

Coordinate2D = Tuple[int, int]
Coordinate3D = Tuple[int, int, int]
ColorRGB = Tuple[int, int, int]


def image_stacks(img_bg: str, img_front: str, img_out: str, coordinate_paste: Coordinate2D):

    M_img = Image.open(img_bg)
    S_img = Image.open(img_front)

    M_img = M_img.convert("RGBA")
    S_img = S_img.convert("RGBA")
    _, _, _, s_a = S_img.split()

    M_img.paste(S_img, coordinate_paste, mask=s_a)

    M_img.save(img_out)
    M_img.close()
    S_img.close()
    pass


def image_txt(img_bg: str, txt: str, coordinate_func: BinFunc[Coordinate2D, Coordinate2D, Coordinate2D], img_out: str,
              font_family: str, font_size: int, font_color: ColorRGB):
    pic_bg = Image.open(img_bg)
    size_bg = pic_bg.size
    draw = ImageDraw.Draw(pic_bg)

    font = ImageFont.truetype(font=font_family, size=font_size)
    size_txt = font.getsize(txt)

    logger.info({size_bg})
    logger.info({size_txt})
    logger.info(coordinate_func(size_bg, size_txt))
    draw.text(xy=coordinate_func(size_bg, size_txt),
              text=txt, fill=font_color, font=font)

    pic_bg.save(img_out)
    pic_bg.close()
    pass
