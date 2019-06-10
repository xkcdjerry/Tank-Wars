import time
import random
import itertools

from locals import *

# 目的：完全整合各类，消除Game类里本该是其它类的冗余代码
# 使得他容易拓展成联网版本（未开始拓展）
pygame.event.set_blocked(None)
pygame.event.set_allowed([pygame.KEYUP, pygame.KEYDOWN, pygame.QUIT, pygame.MOUSEBUTTONDOWN])


class Proxy:
    def __init__(self, dct=None):
        self._dct = {} if dct is None else dct

    def __setattr__(self, key, val):
        if key.startswith("_"):
            super().__setattr__(key, val)
        self._dct[key] = val

    def __getattr__(self, key):
        if key.startswith("_"):
            return super().__getattribute__(key)
        return self._dct[key]


class Char:
    # Father for all player/foes
    pass


class Player(Char):
    OPR = {BLOOD: lambda player: player.set_blood(player.blood+1)}
    STARTS = (MAXWIDTH-80-len(POWERUPS)*40, 15)
    BLOODCOLORS = (GREEN, ORANGE)
    IMGS = (PLAYER0, PLAYER1)
    # LEFT      DOWN      RIGHT     UP        FIRE        MINES

    ALL = (
        (pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_w,
         pygame.K_j, pygame.K_k),
        (pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_UP,
         pygame.K_COMMA, pygame.K_PERIOD)
    )

    def __init__(self, pos, game, cnt=0, oneplayer=False):
        """pos:位置元组 (x,y)
        :type pos: tuple
        :type game: Game
        :type cnt: int
        :type oneplayer: bool


        """
        self.score = 0
        self.cnt = cnt if not oneplayer else 0  # use the green
        self.movekeys = Player.ALL[cnt] if not oneplayer else Player.ALL[0]
        self.blood_xstart = Player.STARTS[cnt] if not oneplayer else Player.STARTS[-1]
        self.effect_xstart = self.blood_xstart if not oneplayer else Player.STARTS[0]
        self.bloodcolor = Player.BLOODCOLORS[cnt] if not oneplayer else RED
        self.endtime = 0
        self.game = game
        self.angle = 0  # up
        self.pos = list(pos)
        self.face = (0, 0)
        self.img = Player.IMGS[cnt]
        self.darttime = 0
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.fire = True
        self.blood = MAXBLOOD
        self.effect = 0b000
        self.stop = [0] * len(POWERUPS)

    def set_blood(self, blood):
        self.blood = min(blood, MAXBLOOD)
        if blood > MAXBLOOD:
            self.add_effect(SHIELD, 10)

    def add_effect(self, effect, t):
        self.effect |= effect
        index = index_effect(effect)
        self.stop[index] = max(time.time()+t, self.stop[index]+t)

    def stop_effect(self, effect):
        if self.effect & effect:
            self.effect -= effect
        self.stop[index_effect(effect)] = 0

    def update(self, down_keys):
        going = []
        k_left, k_down, k_right, k_up, k_fire, k_mine = self.movekeys
        for i in range(len(self.stop)):
            if self.stop[i] < time.time():
                self.stop_effect(POWERUPS[i])

        if self.effect & SWIFT:
            speed = SPEED*2
        else:
            speed = SPEED
        if time.time() >= self.darttime:
            self.fire = True
        if k_fire in down_keys:
            if self.fire:
                self.game.bullets.append(
                    Bullet(self.pos,
                           (BUL_SPD*self.face[0], BUL_SPD*self.face[1]),
                           [],
                           cache("BULLET", self.angle),
                           self, self.effect & MAGAZINE))

                self.fire = False
                if not self.effect & MAGAZINE:
                    self.darttime = time.time() + 1
                else:
                    self.darttime = time.time() + 0.1
        if k_mine in down_keys:
            if self.fire or self.effect & MAGAZINE:
                self.game.bullets.append(
                    Bullet(self.pos, (0, 0),
                           [],
                           MINE,
                           self, True))
                if not self.effect & MAGAZINE:
                    self.fire = False
                    self.darttime = time.time() + 0.1
        if k_up in down_keys:
            self.pos[1] -= speed
            going.append(UP)
            if k_down in down_keys:
                del down_keys[k_down]  # 不能同时向上和下走
        if k_down in down_keys:
            self.pos[1] += speed
            going.append(DOWN)
            if k_up in down_keys:
                del down_keys[k_up]  # 不能同时向上和下走
        if k_left in down_keys:
            self.pos[0] -= speed
            going.append(LEFT)
            if k_right in down_keys:
                del down_keys[k_right]  # 不能同时向左和右走
        if k_right in down_keys:
            self.pos[0] += speed
            going.append(RIGHT)
            if k_left in down_keys:
                del down_keys[k_left]  # 不能同时向左和右走
        # print(going)
        if not going:
            pass
        elif len(going) == 1:
            self.angle, self.face = ANGLE_DICT[going[0]]
        elif len(going) == 2:
            self.angle, self.face = ANGLE_DICT_2[frozenset(going)]
        else:  # UNREACHABLE
            assert (), "Unreachable"

        self.rect.center = self.pos
        if self.rect.left < 0:
            self.rect.left = SPEED  # 防卡住
            if k_left in down_keys:
                del down_keys[k_left]  # 不能再走了！
        if self.rect.top < 0:
            self.rect.top = SPEED  # 防卡住
            if k_up in down_keys:
                del down_keys[k_up]  # 不能再走了！
        if self.rect.bottom > MAXHIGHT:
            self.rect.bottom = MAXHIGHT - SPEED  # 防卡住
            if k_down in down_keys:
                del down_keys[k_down]  # 不能再走了！
        if self.rect.right > MAXWIDTH:
            self.rect.right = MAXWIDTH - SPEED  # 防卡住
            if k_down in down_keys:
                del down_keys[k_right]  # 不能再走了！
        targets = self.game.foes+[(i if (not i.player) else None)
                                  for i in self.game.bullets]
        for i in self.game.bullets:
            if i.player:
                i.targets = targets
        self.render()

    def render(self):
        if time.time() < self.endtime:
            return
        self.img = cache("PLAYER%d" % self.cnt, self.angle)
        self.rect = self.img.get_rect()
        self.rect.center = self.pos

    def blit(self, win):
        if self.effect & SWIFT:
            img, rect = get_img_and_rect("SWIFT", self.angle, self.pos)
            win.blit(img, rect)
        win.blit(self.img, self.rect)
        if self.effect & SHIELD:
            img, rect = get_img_and_rect("SHIELD", self.angle, self.pos)
            win.blit(img, rect)

    def draw_blood(self, win):
        for i in range(self.blood):  # draw health bars
            pygame.draw.rect(win, self.bloodcolor, (self.blood_xstart, 15+(10*MAXBLOOD) - i*20, 30, 20))
        for i in range(MAXBLOOD):  # draw white outsides
            pygame.draw.rect(win, WHITE,
                             (self.blood_xstart, 15+(10*MAXBLOOD) - i*20, 30, 20), 1)

    def draw_effects(self, win):
        t = time.time()
        for i in range(len(self.stop)):
            img = IMG[POWERUPS[i]]
            rect = img.get_rect()
            rect.center = (self.effect_xstart+80+40*i, 30)
            pygame.draw.rect(win, WHITE, rect)
            win.blit(img, rect)
            pygame.draw.rect(win, BLACK, rect, 1)
            if self.stop[i] >= time.time():
                img2, rect2 = mktext(NUMFONT, str(round(self.stop[i]-t, 1)),
                                     center=(self.effect_xstart+80+40*i,
                                             70), _bg=False)
                pygame.draw.rect(win, WHITE, rect2)

            else:
                img2 = IMG["CROSS"]
                rect2 = img2.get_rect()
                rect2.center = (self.effect_xstart+80+40*i, 70)

            win.blit(img2, rect2)
            pygame.draw.rect(win, BLACK, rect2, 1)

    def draw_score(self, win):
        text = "Player %d Kills : %d" % (self.cnt+1, self.score)
        img, rect = mktext(NUMFONT, text, _bg=False)
        rect.center = (self.effect_xstart+80, 100)
        win.blit(img, rect)

    def add_stuff(self, typeof):
        return Player.OPR[typeof](self)


class Packet:
    def __init__(self, pos, typeof, game):
        self.type = typeof
        self.pos = pos
        self.img = IMG[typeof]
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.game = game
        self.index = index_effect(typeof)

    def collide(self):
        game = self.game
        for i in game.characters:
            if issubclass(i.__class__, Char) and self.rect.colliderect(i.rect):
                i.add_effect(self.type, 10)
                return i


class Stuff:
    def __init__(self, pos, typeof, game):
        self.type = typeof
        self.pos = pos
        self.game = game
        self.img = IMG[typeof]
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.game = game

    def collide(self):
        game = self.game
        for i in game.characters:
            if issubclass(i.__class__, Char) and self.rect.colliderect(i.rect):
                i.add_stuff(self.type)
                return i


class Ai(Char):
    def __init__(self, game, ratio):
        self.robot = NullBot()
        self.game = game
        self.cnt = 0
        self.ratio = ratio

    def update(self):
        self.cnt += 1
        if self.robot.effect & SWIFT:
            self.robot.pos[0] += self.robot.spd[0]*2
            self.robot.pos[1] += self.robot.spd[1]*2
        else:
            self.robot.pos[0] += self.robot.spd[0]
            self.robot.pos[1] += self.robot.spd[1]
        if (self.cnt % ((10//self.ratio) if
                        self.robot.effect & MAGAZINE
                        else (100//self.ratio)) ==
            random.randint(0, 9//self.ratio if self.robot.effect & MAGAZINE
                           else 99//self.ratio)):

            targets = self.game.players
            self.game.bullets.append(Bullet(self.robot.pos, (-BUL_SPD, 0),
                                            targets, cache("BULLET", 90)))
        for i in range(len(self.robot.stop)):
            if self.robot.stop[i] < time.time():
                self.robot.stop_effect(POWERUPS[i])


class NullBot(Char):
    def __getattribute__(self, name):
        raise NotImplementedError

    def __setattr__(self, name, obj):
        raise NotImplementedError


class Enemy(Char):
    def __init__(self, ai, pos, spd):
        self.ai = ai
        self.killer = Proxy({"score":0})
        self.pos = list(pos)
        self.spd = spd
        ai.robot = self
        self.angle = 90
        self.img = cache("ENEMY", self.angle)
        self.rect = self.img.get_rect()
        self.effect = 0b000
        self.stop = [0]*len(POWERUPS)
        self.update()

    def update(self):
        self.ai.update()
        self.render()

    def add_effect(self, effect, t):
        self.effect |= effect
        index = index_effect(effect)
        self.stop[index] = max(time.time()+t, self.stop[index]+t)

    def stop_effect(self, effect):
        if self.effect & effect:
            self.effect -= effect
        self.stop[index_effect(effect)] = 0

    def add_stuff(self, typeof):
        pass

    def render(self):
        self.rect.center = self.pos

    def blit(self, win):
        if self.effect & SWIFT:
            img, rect = get_img_and_rect("SWIFT", self.angle, self.pos)
            win.blit(img, rect)
        win.blit(self.img, self.rect)
        if self.effect & SHIELD:
            img, rect = get_img_and_rect("SHIELD", self.angle, self.pos)
            win.blit(img, rect)


class Bullet:
    def __init__(self, pos, spd, targets, img=cache("BULLET"),
                 player=None, mine_or_powerup=False):
        self.anti_shield = mine_or_powerup  # mines
        self.img = img
        self.player = player
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.pos = list(pos)
        self.spd = spd
        self.targets = targets

    def update(self):
        self.pos[0] += self.spd[0]
        self.pos[1] += self.spd[1]
        self.rect.center = self.pos
        for i in self.targets:
            if i is not None and self.rect.colliderect(i.rect) and i != self:
                return i

        return False  # hit nothing


class Game:
    def __init__(self, player_pos_tup):
        self.ratio = 1
        self.player_cnt = len(player_pos_tup)
        self.many_player = self.player_cnt > 1
        self.pos_cache = player_pos_tup[:]
        self.window = get_window()
        self.down_keys = {}
        self.bullets = []
        self.stuff = []
        self.foes = []
        self.packs = []
        self.dead_players = []
        self.new()

    def new(self):
        # this is called to rewind a game
        self.clock = pygame.time.Clock()
        self.count = 0
        self.best = get_best()
        if len(self.pos_cache) == 1:
            self.players = [Player(self.pos_cache[0], self, oneplayer=True)]
        else:
            self.players = [Player(i, self, cnt) for cnt, i in enumerate(self.pos_cache)]
        self.down_keys.clear()
        self.bullets.clear()
        self.stuff.clear()
        self.foes.clear()
        self.dead_players.clear()
        self.bonus = 0
        self.score = 0
        self.window.blit(BG, (0, 0))
        pygame.display.update()
        self.characters = [*self.players]
        self.packs.clear()
        # keep pos_cache,window and clock

    @staticmethod
    def stop():
        pygame.quit()

    def render(self):
        self.window.blit(BG, (0, 0))  # back ground
        for i in self.dead_players:
            self.window.blit(TOMB, i.rect)
        for i in self.bullets:
            self.window.blit(i.img, i.rect)
            if i.rect.right < 0:
                self.bullets.remove(i)
        for i in self.foes:
            if i.img != EXPLODE:
                i.update()
            else:
                killer = i.killer
                for j in self.foes:
                    if j.rect.colliderect(i.rect) and not j.effect & SHIELD:
                        self.explode(j)
                        j.killer = killer
                        # merge_stoptime(self.player.stop,j.stop)
                        self.bonus += 5
                    else:
                        j.stop_effect(SHIELD)
                for j in self.bullets:
                    if j.rect.colliderect(i.rect):
                        self.bonus += 1
                        self.bullets.remove(j)
            i.blit(self.window)
            if i.rect.right < 0:
                self.foes.remove(i)
        for i in itertools.chain(self.packs, self.stuff):
            self.window.blit(i.img, i.rect)

        for i in self.players:
            i.blit(self.window)
        img, rect = mktext(NUMFONT, "Score:%i" % self.score,
                           center=(WIDTH//2, 40), _bg=False)

        self.window.blit(img, rect)
        img2, rect2 = mktext(NUMFONT, "Best Score:%i" %
                             self.best, center=(WIDTH//2, 80), _bg=False)

        self.window.blit(img2, rect2)
        for i in self.players:
            i.draw_effects(self.window)
            i.draw_blood(self.window)
        if self.many_player:
            for i in self.players:
                i.draw_score(self.window)
        pygame.display.update()

    def add_entitys(self):
        ratio = self.ratio
        i = self.count
        if i % (20//(ratio*(0.5+self.player_cnt*0.5))) == random.randint(0, (20//(ratio*(0.5+self.player_cnt*0.5))-1)):
            foe = Enemy(Ai(self, ratio),
                        (WIDTH+10, random.randint(0, MAXHIGHT)),
                        (-SPEED, 0))
            self.foes.append(foe)
            self.characters.append(foe)
        if i % (100//ratio) == random.randint(0, (100//ratio)-1):
            packet = Packet([random.randint(0, MAXWIDTH), random.randint(
                0, MAXHIGHT)], random.choice(POWERUPS), self)
            self.packs.append(packet)
        if i % (300//ratio) == random.randint(0, (300//ratio)-1):
            stuff = Stuff([random.randint(0, MAXWIDTH), random.randint(
                0, MAXHIGHT)], random.choice(STUFF), self)
            self.stuff.append(stuff)

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                save_best(self.best)
                return True, self.fps  # stop!

            elif event.type == pygame.KEYDOWN:
                self.down_keys[event.key] = True
            elif event.type == pygame.KEYUP:
                if event.key in self.down_keys:
                    del self.down_keys[event.key]


    def run(self):
        global BUL_SPD, SPEED
        running = True
        self.count = 0
        t = 0
        while running:

            self.count += 1

            fps = self.count/t if self.count > 10 else FPS  # avoid Bad averages
            ratio = FPS/fps
            self.fps = fps
            BUL_SPD = INIT_BUL_SPD*ratio
            SPEED = INIT_SPEED*ratio
            self.ratio = ratio
            self.add_entitys()

            temp = self.handle_events()
            if temp:  # stop
                return temp

            for i in self.players:
                i.update(self.down_keys)

            for j in self.packs:
                if j.collide():
                    self.packs.remove(j)
            for j in self.stuff:
                if j.collide():
                    self.stuff.remove(j)
            for j in self.foes:
                if j.img == EXPLODE:
                    j.killer.score += 1
                    self.kill_foe(j)
                for i in self.players:
                    if i.effect & SHIELD and j.rect.colliderect(i.rect):
                        if (j.effect & SHIELD and not
                                i.effect & (SHIELD | SWIFT) ==
                                (SHIELD | SWIFT)):
                            continue
                        self.explode(j)
                        i.effect |= j.effect
                        merge_stoptime(i.stop, j.stop)
            for j in self.bullets:
                if j not in self.characters:
                    self.characters.append(j)
                hit = j.update()

                if not hit:
                    continue
                elif hit in self.players:
                    if not hit.effect & SHIELD:
                        hit.blood -= 1
                        hit.add_effect(SHIELD, 3)
                    else:
                        hit.stop[index_effect(SHIELD)] -= 10
                    if hit.blood <= 0:
                        self.players.remove(hit)
                        self.dead_players.append(hit)
                        if len(self.players) == 0:
                            self.window.blit(BG, (0, 0))  # back ground
                            self.explode(hit)
                            pygame.time.wait(500)  # clear the que
                            pygame.event.get()
                            self.gameover(self.score)
                            stop = waitforkey()
                            save_best(self.best)
                            return stop, self.fps

                elif hit in self.foes:
                    if hit.effect & SHIELD and not j.anti_shield:
                        self.bullets.remove(j)
                        hit.stop_effect(SHIELD)
                        continue
                    self.explode(hit)
                    if j.player:
                        hit.killer = j.player
                        j.player.effect |= hit.effect
                        j.player.score += 1
                        merge_stoptime(j.player.stop, hit.stop)
                        self.bonus += 10
                elif hit in self.bullets:
                    self.bullets.remove(hit)
                    if j.player:
                        self.bonus += 10
                self.bullets.remove(j)

            self.score = round(self.count/fps)+self.bonus
            self.best = max(self.best, self.score)
            self.render()

            t += self.clock.tick(MAX_FPS)/1000   # milliseconds too seconds

    def gameover(self, score):
        # The game over code
        surf, rect = mktext(GAMEOVERFONT,
                            "Game Over,Your score:%.2f" % score,
                            _bg=False)
        self.window.blit(surf, rect)
        surf2, rect2 = mktext(GAMEOVERFONT, "Press any key to continue.",
                              center=[MID[0], MID[1]+TEXTSIZE+20], _bg=False)
        self.window.blit(surf2, rect2)
        surf3, rect3 = mktext(GAMEOVERFONT, "Best score:%.2f" % self.best,
                              center=[MID[0], MID[1]+TEXTSIZE*2+20*2], _bg=False)
        self.window.blit(surf3, rect3)
        pygame.display.update()

    def explode(self, char, change_rect=True):
        char.img = EXPLODE
        if change_rect:
            pos = char.rect.center
            char.rect = char.img.get_rect()
            char.rect.center = pos
            rect = char.rect
        else:
            pos = char.rect.center
            rect = char.img.get_rect()
            rect.center = pos
        self.window.blit(char.img, rect)
        pygame.display.flip()

    def kill_foe(self, foe):
        # Remove the foe
        self.foes.remove(foe)
        self.characters.remove(foe)
