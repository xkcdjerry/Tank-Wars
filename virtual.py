import os

import pygame

PATH = os.path.dirname(__file__)
BASE = os.path.join(PATH,"Bin")
WIDTH = HIGHT = None
SMMOTH = True


def debug():
    print(WIDTH, HIGHT, SMMOTH)


def config(width, hight, smmoth=None):
    global WIDTH, HIGHT, SMMOTH
    WIDTH = width
    HIGHT = hight
    SMMOTH = SMMOTH if smmoth is None else bool(smmoth)


def clear():
    global WIDTH, HIGHT, SMMOTH
    WIDTH = HIGHT = None
    SMMOTH = True


def shiftsize(img):
    rect = img.get_rect()
    width = rect.width if WIDTH is None else WIDTH
    hight = rect.height if HIGHT is None else HIGHT
    func = pygame.transform.smoothscale if SMMOTH else pygame.transform.scale
    return func(img, (width, hight))


def _load(s):
    return pygame.image.load(transform_name(s))


def load(s, ignore_config=False):
    # debug()
    img = _load(s)
    if ignore_config:
        return img
    else:
        return shiftsize(img)


def init():
    return pygame.init()


def transform_name(s):
    return os.path.join(BASE, s)
