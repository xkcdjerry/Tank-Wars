import sys
import os

import pygame

from classes import Game
from locals import MID, FPS, BG, SIZE, SELECT_PLAYER_IMGS, get_window, TITLE


PATH = os.path.dirname(__file__)


def getname():
    i = 1
    fmt = os.path.join(PATH, "..", "bugreport%i.txt")
    while os.path.isfile(fmt % i):
        i += 1
    return fmt % i


def select():
    win = get_window()
    win.blit(BG, (0, 0))
    size = SIZE[0]
    player_lst = []
    img = TITLE
    rect = img.get_rect()
    rect.centerx = size//2
    rect.centery = size//20
    win.blit(img, rect)
    for i in range(2):
        y = size//5 + i*size//5
        img = SELECT_PLAYER_IMGS[i]
        rect = img.get_rect()
        rect.center = (size//2, y)
        player_lst.append((img, rect))
        win.blit(img, rect)
    pygame.display.flip()
    ans = None
    while ans is None:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif i.type == pygame.MOUSEBUTTONDOWN:
                for j in range(len(player_lst)):
                    if player_lst[j][1].collidepoint(i.pos):
                        ans = j+1
    pygame.event.clear()
    return ans


def _main():
    stop = False
    old_num_players = -1
    game = Game(())
    while not stop:
        num_players = select()
        if num_players == old_num_players:
            game.new()
        else:
            game = Game((MID,) * num_players)
            old_num_players = num_players
        try:
            stop, fps_real = game.run()
            frame_ratio = FPS/fps_real

        except BaseException as e:
            # makes sure it's shut down right
            game.stop()
            raise
        print('RATIO:', frame_ratio, 'FPS:', fps_real)
        game.new()
        game.window.blit(BG, (0, 0))
    game.stop()
    return game


def main():
    try:
        _main()
    except Exception as e:
        import traceback
        print("Error Found...")
        print("Shutting down program...")
        s = traceback.format_exc()
        with open(getname(), "w") as f:
            f.write(s)
            f.write("\n\n")
            f.write(str(e))
        traceback.print_exc()
        return e
    except (KeyboardInterrupt, SystemExit):  # ignored
        return


if __name__ == '__main__':
    main()
