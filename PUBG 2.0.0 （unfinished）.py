import random
import time
import os
import pickle

import pygame

from classes import *


pygame.init()


def main():
    stop = False
    game = Game((MID,))
    while not stop:
        try:
            stop, fps_real = game.run()
            frame_ratio = FPS/fps_real

        except BaseException:
            # makes sure it's shut down right
            pygame.quit()
            raise
        print('RATIO:', frame_ratio, 'FPS:', fps_real)
        game.new()
        game.window.blit(BG, (0, 0))
    game.stop()
    return game


if __name__ == '__main__':
    cached_game = main()
    # for testing
