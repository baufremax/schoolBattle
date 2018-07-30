#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import pygame
import random
from os import path

from constant import Constant

## assets folder
img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')

font_name = pygame.font.match_font('arial')

cons = Constant()

def main_menu():
    global screen
    cons = Constant()
    menu_song = pygame.mixer.music.load(path.join(sound_folder, "menu.mp3"))
    pygame.mixer.music.set_volume(5)
    pygame.mixer.music.play(-1)

    title = pygame.image.load(path.join(img_dir, "main.jpg")).convert()
    title = pygame.transform.scale(title, (cons.WIDTH, cons.HEIGHT), screen)

    screen.blit(title, (0,0))
    draw_text(screen, "School Battle", 72, cons.WIDTH/2, cons.HEIGHT/2 - 80, cons.BLACK)
    pygame.display.update()

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
        elif ev.type == pygame.QUIT:
                pygame.quit()
                quit() 
        else:
            draw_text(screen, "Press [ENTER] To Begin", 30, cons.WIDTH/2, cons.HEIGHT/2, cons.BLACK)
            draw_text(screen, "or [Q] To Quit", 30, cons.WIDTH/2, (cons.HEIGHT/2)+40, cons.BLACK)
            draw_text(screen, "Press [SPACE] To Shoot", 30, cons.WIDTH/2, cons.HEIGHT/2 + 80, cons.BLACK)
            pygame.display.update()

    # Hide the mouse cursor.
    pygame.mouse.set_visible(False)

    screen.fill(cons.BLACK)
    screen.blit(background, background_rect)
    draw_text(screen, "GET READY!", 40, cons.WIDTH/2, cons.HEIGHT/2, cons.BLACK)
    pygame.display.update()
    pygame.event.pump()
    pygame.time.wait(1000)
    for i in range(3):
        screen.fill(cons.BLACK)
        screen.blit(background, background_rect)
        draw_text(screen, str(3 - i), 40, cons.WIDTH/2, cons.HEIGHT/2, cons.BLACK)
        pygame.display.update()
        pygame.event.pump()
        pygame.time.wait(1000)
    

def draw_text(surf, text, size, x, y, color = cons.WHITE):

    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, False, color)       # True denotes the font to be anti-aliased 
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    # if pct < 0:
    #     pct = 0
    pct = max(pct, 0) 
    fill = (pct / 100) * cons.BAR_LENGTH
    outline_rect = pygame.Rect(x, y, cons.BAR_LENGTH, cons.BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, cons.BAR_HEIGHT)
    pygame.draw.rect(surf, cons.GREEN, fill_rect)
    pygame.draw.rect(surf, cons.WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect= img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def newmob(score):
    mob_element = Mob(score)
    all_sprites.add(mob_element)
    mobs.add(mob_element)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self, score):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        ## scale the player img down
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(cons.BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = cons.WIDTH / 2
        self.rect.bottom = cons.HEIGHT - 10
        self.speedx = 0 
        self.shield = 100

        self.level = 1

        self.shoot_delay = 500

        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self, score):
        # update shooting speed
        self.level = int(score / 500) + 1
        self.shoot_delay = 700 - self.level * 50
        if self.shoot_delay < 200:
            self.shoot_delay = 200

        if self.power >=2 and pygame.time.get_ticks() - self.power_time > cons.POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = cons.WIDTH / 2
            self.rect.bottom = cons.HEIGHT - 30

        self.speedx = 0 
        self.speedy = 0  

        keystate = pygame.key.get_pressed()     
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5
        elif keystate[pygame.K_UP]:
            self.speedy = -5
        elif keystate[pygame.K_DOWN]:
            self.speedy = 5

        #Fire weapons by holding spacebar
        if keystate[pygame.K_SPACE]:
            self.shoot()

        ## check for the borders at the left and right
        if self.rect.right > cons.WIDTH:
            self.rect.right = cons.WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > cons.HEIGHT and not self.hidden:
            self.rect.bottom = cons.HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def shoot(self):
        ## tell the bullet where to spawn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shooting_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sound.play()

            """ MOAR POWAH """
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top) # Missile shoots from center of ship
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
                shooting_sound.play()
                # missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (cons.WIDTH / 2, cons.HEIGHT + 200)

# defines the opposite schools
class Mob(pygame.sprite.Sprite):
    def __init__(self, score):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(school_images)
        self.image_orig.set_colorkey(cons.BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .90 / 3)
        self.rect.x = random.randrange(0, cons.WIDTH - self.rect.width)
        self.rect.y = random.randrange(-20, -10)

        self.level = int(score / 1000)

        self.speedy = random.randrange(3 * int(self.level / 2 + 1), 6 * int(self.level / 2 + 1))        ## for randomizing the speed of the Mob


        ## randomize the movements
        self.speedx = random.randrange(-3 * int(self.level / 5 + 1), 3 * int(self.level / 5 + 1))

        ## adding rotation to the mob element
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()  ## time when the rotation has to happen
        
    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50: # in milliseconds
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360 
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self, score):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if (self.rect.top > cons.HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > cons.WIDTH + 20):
            self.rect.x = random.randrange(0, cons.WIDTH - self.rect.width)
            self.rect.y = random.randrange(-20, -10)
            self.speedy = random.randrange(1 * int(self.level / 2 + 1), 4 * int(self.level / 2 + 1))
            self.speedx = random.randrange(-2 * int(self.level / 2 + 1), 2 * int(self.level / 2 + 1))

# defines the sprite for Powerups
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(cons.BLACK)
        self.rect = self.image.get_rect()
        # place the bullet according to the current position of the player
        self.rect.center = center
        self.speedy = 2

    def update(self, score):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        # kill the sprite after it moves over the top border
        if self.rect.top > cons.HEIGHT:
            self.kill()

# defines the sprite for bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(cons.BLACK)
        self.rect = self.image.get_rect()
        # place the bullet according to the current position of the player
        self.rect.bottom = y 
        self.rect.centerx = x
        self.speedy = -10

    def update(self, score):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        # kill the sprite after it moves over the top border
        if self.rect.bottom < 0:
            self.kill()

## Fire BoYa Tower
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(cons.BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self, score):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

## Initiaize the screen
cons = Constant()
pygame.init()
pygame.mixer.init()  # For sound
screen = pygame.display.set_mode((cons.WIDTH, cons.HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()     # For syncing the FPS

# Load all game images

background = pygame.image.load(path.join(img_dir, 'schoolField.jpg')).convert()
background_rect = background.get_rect()

player_img = pygame.image.load(path.join(img_dir, 'playerSchool.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(cons.BLACK)

bullet_img = pygame.image.load(path.join(img_dir, 'volume.png')).convert()

missile_img = pygame.image.load(path.join(img_dir, 'tower.png')).convert_alpha()

school_images = []

school_list = [
    'School_big1.png',
    'School_big2.png',
    'School_med1.png',
    'School_med2.png',
    'School_med3.png',
    'School_small1.png',
    'School_small2.png',
    'School_tiny1.png',
]

for image in school_list:
    school_images.append(pygame.image.load(path.join(img_dir, image)).convert())

# school explosion
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(cons.BLACK)
    # resize the explosion
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    # player explosion
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(cons.BLACK)
    explosion_anim['player'].append(img)

# load power ups
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'plus_sign.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()

### Load all game sounds
shooting_sound = pygame.mixer.Sound(path.join(sound_folder, 'bullet.wav'))
missile_sound = pygame.mixer.Sound(path.join(sound_folder, 'rocket.ogg'))
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder, sound)))
## main background music

pygame.mixer.music.set_volume(0.2)      ## simmered the sound down a little

player_die_sound = pygame.mixer.Sound(path.join(sound_folder, 'rumble1.ogg'))


#########################################################################
## Game loop

running = True
menu_display = True
screen_refresh = False

while running:
    if menu_display:
        main_menu()

        #Stop menu music
        pygame.mixer.music.stop()
        #Play the gameplay music
        pygame.mixer.music.load(path.join(sound_folder, 'battle.mp3'))
        pygame.mixer.music.play(-1)     # makes the gameplay sound in an endless loop
        
        menu_display = False

        #### Score board variable
        score = 0

        ## group all the sprites together for ease of update
        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)

        

        ## spawn a group of schools
        mobs = pygame.sprite.Group()
        for i in range(8):      ## 8 schools
            newmob(score)

        ## group for bullets
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
    
    #1 Process input/events
    clock.tick(cons.FPS)     ## make the loop run at the same speed all the time
    for event in pygame.event.get():       

        if event.type == pygame.QUIT:
            running = False

        # Press ESC or Q to exit game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
               running = False

    #2 Update
    all_sprites.update(score)


    ## check if a bullet hit a school
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius         ## give different scores for hitting big and small schools
        random.choice(expl_sounds).play()   # to make the sound more rhythmed.
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob(score)        ## make a new school

    ## check if the player collides with the school
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob(score)
        if player.shield <= 0: 
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            # running = False     ## GAME OVER 3:D
            player.hide()
            player.lives -= 1
            player.shield = 100
            screen_refresh = True

    ## if the player hit a power up
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()

    ## if player died and the explosion has finished, end game
    if player.lives == 0 and  not death_explosion.alive():
        draw_text(screen, "You Lose...", 48, cons.WIDTH/2, cons.HEIGHT/2, cons.YELLOW)
        # fail_sound = pygame.mixer.music.load(path.join(sound_folder, "failure.mp3"))
        # pygame.mixer.music.play(1)
        menu_display = True
        pygame.display.update()
        pygame.event.pump()
        pygame.time.wait(1000)

    #3 Draw/render
    # screen.fill(cons.BLACK)
    screen.blit(background, background_rect)
    # screen.fill(cons.WHITE)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 32, cons.WIDTH / 2, 10, cons.BLACK)     ## 10px down from the screen
    draw_shield_bar(screen, 5, 5, player.shield)

    # Draw lives
    draw_lives(screen, cons.WIDTH - 100, 5, player.lives, player_mini_img)

    ## Done after drawing everything to the screen
    pygame.display.flip()       

pygame.quit()
