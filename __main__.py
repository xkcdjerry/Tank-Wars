import os
import sys

import pygame

from classes import Game
from locals import MID, FPS, BG, WIDTH, HIGHT, SELECT_PLAYER_IMGS, get_window, TITLE, save_best
from utils import errors


win = get_window()

PATH = os.path.dirname(__file__)
ERR_HANDLER = errors.ErrorHandler()






def select_play_opt():
    """
ask the player which option to choose
(currently, he can choose one player or two players)


    :return: int
    """
    win.blit(BG, (0, 0))
    options = []

    # blit on the title
    img = TITLE
    rect = img.get_rect()
    rect.centerx = WIDTH // 2
    rect.centery = HIGHT // 10
    win.blit(img, rect)

    # blit the options
    opts_max = len(SELECT_PLAYER_IMGS)

    for i in range(opts_max):
        y = HIGHT // (opts_max+1) + i * HIGHT // (opts_max+1)
        # TODO:some code to calculate the y coord of a options,I am going to clean it up someday

        # blit one option
        img = SELECT_PLAYER_IMGS[i]
        rect = img.get_rect()
        rect.center = (WIDTH // 2, y)
        options.append((img, rect))
        win.blit(img, rect)
    pygame.display.flip()
    selected_option = None
    while selected_option is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for index, opt in enumerate(options):
                    if opt[1].collidepoint(event.pos):
                        selected_option = index
    pygame.event.clear()
    return selected_option


def _main():
    """
_main()
runs the game and prints analysis each time

uses select_player_opt to ask the player which option to choose
(options can be seen in the docs for select_player_opt)
"""

    # hack for setting all to order before importing classes
    stop = False
    last_option = -1
    game = Game(())
    while not stop:
        new_option = select_play_opt()
        if new_option == last_option:
            game.new()
        else:
            if 0 <= new_option < 2:
                player_cnt = new_option+1
                game = Game((MID,) * player_cnt)
            last_option = new_option
        try:
            stop, fps_real = game.run()
            frame_ratio = FPS / fps_real

        except BaseException:
            # makes sure it's shut down right
            save_best(game.best)
            game.stop()
            # and then pass the exception along
            raise
        print('RATIO: %.5f FPS: %.5f' % (frame_ratio, fps_real))
        game.new()
        game.window.blit(BG, (0, 0))
    game.stop()
    return game


def main():
    try:
        _main()
    except Exception as e:
        return ERR_HANDLER.handle(e)
    except (KeyboardInterrupt, SystemExit) as e:  # ignored
        return e


if __name__ == '__main__':
    main()
