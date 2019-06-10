import os
import pickle
import json

import pygame

import virtual

virtual.init()

with open("config.json") as jsonfile:
    dct = json.load(jsonfile)
VERSION = dct["version"]
BESTSCOREFILE = virtual.transform_name('bestscore.dat')
SIZE = WIDTH, HIGHT = 1300, 800
MID = WIDTH/2, HIGHT/2
MAXHIGHT = HIGHT-1
MAXWIDTH = WIDTH-1

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (250, 210, 80)

FPS = 30
MAX_FPS = 10000
TEXTSIZE = 80
NUMSIZE = 20
INIT_SPEED = 3
INIT_BUL_SPD = 7
SPEED = INIT_SPEED
BUL_SPD = INIT_BUL_SPD
BLOWUPTIME = 0.1  # secs
MAXBLOOD = 3

SHIELD = 1
MAGAZINE = 2
SWIFT = 4
POWERUPS = [SHIELD, MAGAZINE, SWIFT]

BLOOD = 3
STUFF = [BLOOD]

CHAR_SIZE = 60
ICON = virtual.load("icon.png")

virtual.config(CHAR_SIZE, CHAR_SIZE)
PLAYER0 = virtual.load("player-0.png")
PLAYER1 = virtual.load("player-1.png")
ENEMY = virtual.load("enemy.png")
TOMB = virtual.load("dead_player.png")
virtual.clear()

TITLE = virtual.load("game_title.png")
MINE = virtual.load("mine.png")
SELECT_PLAYER_IMGS = (virtual.load("one_player.png"), virtual.load("two_players.png"))
EXPLODE = virtual.load("explode.png")
BG = pygame.transform.smoothscale(virtual.load("bg.png"), SIZE)
GAMEOVERFONT = pygame.font.Font("freesansbold.ttf", TEXTSIZE)
NUMFONT = pygame.font.Font("freesansbold.ttf", NUMSIZE)
IMG = {"PLAYER0": PLAYER0,
       "PLAYER1": PLAYER1,
       "TOMB": TOMB,
       "ENEMY": ENEMY,
       "MINE": MINE,
       "BULLET": virtual.load("bullet.png"),
       "EXPLODE": EXPLODE,
       "SHIELD": virtual.load("shield.png"),
       "MAGAZINE": virtual.load("magazine.png"),
       "SWIFT": virtual.load("swift.png"),
       "CROSS": virtual.load("cross.png"),
       "BLOOD": virtual.load("blood.png")}
SMALL_SIZE = 40
IMG[BLOOD] = pygame.transform.smoothscale(
    IMG["BLOOD"], (SMALL_SIZE, SMALL_SIZE))
IMG[MAGAZINE] = pygame.transform.smoothscale(
    IMG["MAGAZINE"], (SMALL_SIZE, SMALL_SIZE))
IMG[SWIFT] = pygame.transform.smoothscale(
    IMG["SWIFT"], (SMALL_SIZE, SMALL_SIZE))
IMG[SHIELD] = pygame.transform.smoothscale(
    IMG["SHIELD"], (SMALL_SIZE, SMALL_SIZE))

UP = "UP"
DOWN = "DOWN"
RIGHT = "RIGHT"
LEFT = "LEFT"

ANGLE_DICT = {UP: (0, (0, -1)),
              DOWN: (180, (0, 1)),
              RIGHT: (270, (1, 0)),
              LEFT: (90, (-1, 0))}  # anticlockwise
ANGLE_DICT_2 = {frozenset((UP, RIGHT)): (315, (1, -1)),
                frozenset((UP, LEFT)): (45, (-1, -1)),
                frozenset((DOWN, LEFT)): (135, (-1, 1)),
                frozenset((DOWN, RIGHT)): (215, (1, 1))}
picturecache = {}
effectcache = {}


def get_window():
    win = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("War Tanks %s,by xkcdjerry" % VERSION)
    pygame.display.set_icon(ICON)
    return win


def cache(img_name, angle=0):
    if (img_name, angle) in picturecache:
        return picturecache[(img_name, angle)]
    else:
        return_img = pygame.transform.rotate(IMG[img_name], angle)
        picturecache[(img_name, angle)] = return_img
        return return_img


def index_effect(effect):
    if effect in effectcache:
        return effectcache[effect]
    else:
        effect_index = POWERUPS.index(effect)
        effectcache[effect] = effect_index
        return effect_index


def get_img_and_rect(img_name, angle, pos):
    img = cache(img_name, angle)
    rect = img.get_rect()
    rect.center = pos
    return img, rect


def get_best():
    if os.path.isfile(BESTSCOREFILE):
        with open(BESTSCOREFILE, 'rb') as f:
            return pickle.load(f)
    else:
        return 0


def save_best(best):
    with open(BESTSCOREFILE, 'wb') as f:
        return pickle.dump(best, f)


def mktext(font, text, color=BLACK, bg=WHITE, center=MID, _bg=True):
    if _bg:
        surf = font.render(text, True, color, bg)
    else:
        surf = font.render(text, True, color)
    rect = surf.get_rect()
    rect.center = center
    return surf, rect


def waitforkey():
    pygame.event.clear()
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        pygame.event.clear()
        return True  # stop

    if event.type == pygame.KEYDOWN:

        pygame.event.clear()
        return False


def merge_stoptime(stop1, stop2):
    """merge stop1 and stop2 to stop1(IN PLACE)"""
    assert len(stop1) == len(stop2), "different lenth"
    for i in range(len(stop1)):
        stop1[i] = max(stop1[i], stop2[i])
