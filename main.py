import pygame
import random
import os

FPS = 60

# 颜色
BGCOLOR = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# 尺寸
WIDTH = 500
HEIGHT = 600
STONE_COUNT = 8

# 掉落率
DROP_RATE = 1 - 0.8

# 游戏的初始化和创建视窗
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞机大战")
clock = pygame.time.Clock()

###############################################################################
# 载入图片
background_img = pygame.image.load(
    os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(
    os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(
    os.path.join("img", "bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(
        os.path.join("img", f"rock{i}.png")).convert())

pygame.display.set_icon(player_mini_img)

# 制作爆炸特效
expl_anim = {}
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []

# 制作岩石
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    player_expl_img = pygame.image.load(
        os.path.join("img", f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(
    os.path.join("img", "shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()

# 载入字体
font_name = os.path.join('font.ttf')

# 载入音乐
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
pygame.mixer.music.load(os.path.join("sound", "background.mp3"))
pygame.mixer.music.set_volume(0.8)
############################################################################


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)


def draw_health(surf, hp, x, y):
    if hp <= 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x+30*i
        img_rect.y = y
        surf.blit(img, img_rect)


def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "太空生存战！", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "W-A-S-D 移动飞船 SPACE 发射子弹", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "按任意键开始游戏！", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)  # FPS
        # 取得输入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False


#######################################################################################


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50,  38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20

        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0

        self.gun = 1
        self.gun_time = 0

        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 25
        self.speedx = 8
        self.speedy = 5

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and (now-self.gun_time) > 5000:
            self.gun -= 1

        if self.hidden and pygame.time.get_ticks()-self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 25

        # 键盘操控
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_d]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_a]:
            self.rect.x -= self.speedx
        if key_pressed[pygame.K_w]:
            self.rect.y -= self.speedy
        if key_pressed[pygame.K_s]:
            self.rect.y += self.speedy
        # 确保在游戏框内
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.bottom >= HEIGHT-25:
            self.rect.bottom = HEIGHT-25
        if self.rect.top <= 25:
            self.rect.top = 25

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun == 2:
                bulletl = Bullet(self.rect.centerx+8, self.rect.top)
                bulletr = Bullet(self.rect.centerx-8, self.rect.top)
                all_sprites.add(bulletl)
                all_sprites.add(bulletr)
                bullets.add(bulletl)
                bullets.add(bulletr)
                shoot_sound.play()
            elif self.gun == 3:
                bulletl = Bullet(self.rect.centerx+8, self.rect.top)
                bulletm = Bullet(self.rect.centerx, self.rect.top)
                bulletr = Bullet(self.rect.centerx-8, self.rect.top)
                all_sprites.add(bulletl)
                all_sprites.add(bulletm)
                all_sprites.add(bulletr)
                bullets.add(bulletl)
                bullets.add(bulletm)
                bullets.add(bulletr)
                shoot_sound.play()
            elif self.gun == 4 or self.gun == 5:
                bulletl = Bullet(self.rect.centerx+10, self.rect.top)
                bulletm1 = Bullet(self.rect.centerx+5, self.rect.top)
                bulletm2 = Bullet(self.rect.centerx-5, self.rect.top)
                bulletr = Bullet(self.rect.centerx-10, self.rect.top)
                all_sprites.add(bulletl)
                all_sprites.add(bulletm1)
                all_sprites.add(bulletm2)
                all_sprites.add(bulletr)
                bullets.add(bulletl)
                bullets.add(bulletm1)
                bullets.add(bulletm2)
                bullets.add(bulletr)
                shoot_sound.play()
            elif self.gun >= 6:
                bulletl = Bullet(self.rect.centerx+14, self.rect.top)
                bulletm1 = Bullet(self.rect.centerx+7, self.rect.top)
                bulletm2 = Bullet(self.rect.centerx-7, self.rect.top)
                bulletr = Bullet(self.rect.centerx-14, self.rect.top)
                bullet1 = Bullet(self.rect.centerx-25, self.rect.top)
                bullet2 = Bullet(self.rect.centerx+25, self.rect.top)
                all_sprites.add(bulletl)
                all_sprites.add(bulletm1)
                all_sprites.add(bulletm2)
                all_sprites.add(bulletr)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bulletl)
                bullets.add(bulletm1)
                bullets.add(bulletm2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(bulletr)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()


class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # 取消失真叠加
        self.image_ori = random.choice(rock_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = self.rect.width*0.85 / 2

        self.total_degree = 0
        self.rot_degree = random.randrange(-2, 2)
        # 随机生成石头的位置
        self.rect.x = random.randrange(0, WIDTH-self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        self.speedy = random.randrange(2, 10)
        self.speedx = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree %= 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        # 解决定位问题
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self) -> None:
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        self.rotate()
        if self.rect.top >= HEIGHT or self.rect.right <= 0 or self.rect.left >= WIDTH:
            self.rect.x = random.randrange(0, WIDTH-self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(3, 6)
            self.speedx = random.randrange(-1, 1)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -15

    def update(self) -> None:
        self.rect.y += self.speedy
        if self.rect.bottom <= 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self) -> None:
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


#################################################################################


# 游戏循环
show_init = True

pygame.mixer.music.play(-1)
running = True
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        # sprite的初始化
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        scores = 0
        # 创建石头
        for i in range(STONE_COUNT):
            new_rock()
    clock.tick(FPS)  # FPS
    # 取得输入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # 更新游戏
    all_sprites.update()
    # 石头与子弹的碰撞处理
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        scores += round(hit.radius)
        # print(scores)
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        random.choice(expl_sounds).play()
        if random.random() > DROP_RATE:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()

    # 飞机与石头的碰撞处理
    hits = pygame.sprite.spritecollide(
        player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits:
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        new_rock()
        player.health -= hit.radius
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
        if player.lives == 0 and not(death_expl.alive()):
            show_init = True

    # 飞机与道具的碰撞处理
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == "shield":
            shield_sound.play()
            player.health += 20
            if player.health > 100:
                player.health = 100
        if hit.type == "gun":
            gun_sound.play()
            player.gunup()

    # 画面显示
    screen.fill(BGCOLOR)
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    draw_text(screen, f"Score: {scores}", 18, WIDTH/2, 10)
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, player_mini_img, WIDTH-100, 15)
    pygame.display.update()


pygame.quit()
