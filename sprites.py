import pygame as pg
from settings import *
from maps import *
from math import hypot
from random import uniform
import pytweening as tween
import random
import itertools

vec = pg.math.Vector2


def collision_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

def collision_cars(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect2)
        if hits:
            if hits[0].hit_rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].hit_rect.left - sprite.hit_rect.width / 2
            if hits[0].hit_rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].hit_rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect2)
        if hits:
            if hits[0].hit_rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].hit_rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

def shoot(self):
    now = pg.time.get_ticks()
    if now - self.last_shot > WEAPONS[self.weapon]['rate']:
        self.last_shot = now
        pos = self.pos + self.barrel_offset.rotate(-self.rot)
        dir = self.dir.rotate(-self.rot)
        if self.type == 'enemy':
            self.vel += -vec(0, WEAPONS[self.weapon]['kickback'] ).rotate(-self.rot)
        else:
            self.vel += -vec(WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
        for i in range(WEAPONS[self.weapon]['bullet_count']):
            spread = uniform(-WEAPONS[self.weapon]['spread'] ,WEAPONS[self.weapon]['spread'])
            bullet = Bullet(self.game, pos, dir.rotate(spread),self,WEAPONS[self.weapon]['damage'])
            if self.type == 'player':
                self.game.player_bullets.add(bullet)
            else:
                self.game.enemy_bullets.add(bullet)
        sound = random.choice(self.game.weapon_sounds[self.weapon])
        if sound.get_num_channels() > 2:
            sound.stop()
        sound.play()
        if self.weapon != 'pistol':
            MuzzleFlash(self.game, pos)
        self.attacking = True

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_imgs['fist']
        self.img = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.last_shot = 0
        self.rot = 270
        self.health = PLAYER_HEALTH
        self.inside_vehicle = False
        self.attacking = False
        self.weapon = 'fist'
        self.type = 'player'
        self.dir = vec(1,0)
        self.barrel_offset = BARREL_OFFSET
        self.pointer = vec(0,0)
        self.weapon_list = ['fist']

    def get_keys(self):

        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if self.inside_vehicle == False:
            if keys[pg.K_a]:
                self.rot_speed = PLAYER_ROT_SPEED
            if keys[pg.K_d]:
                self.rot_speed = - PLAYER_ROT_SPEED
            if keys[pg.K_UP] or keys[pg.K_w]:
                self.vel = - vec(PLAYER_SPEED, 0).rotate(-self.rot)
            if keys[pg.K_DOWN] or keys[pg.K_s]:
                self.vel = vec(PLAYER_SPEED / 2, 0).rotate(-self.rot)
            if keys[pg.K_RIGHT]:
                self.vel = vec(0, -PLAYER_SPEED / 2).rotate(-self.rot)
            if keys[pg.K_LEFT]:
                self.vel = vec(0, PLAYER_SPEED / 2).rotate(-self.rot)
            if keys[pg.K_SPACE]:
                if self.weapon == 'fist':
                    self.attack()
                if self.weapon != 'fist':
                    shoot(self)
            if not keys[pg.K_SPACE]:
                self.attacking = False


        if self.health <= 0:
            self.game.playing = False

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

    def update(self):
        self.get_keys()
        if self.attacking == True :
            self.img = self.game.player_imgs[self.weapon]
        else:
            self.img = self.game.player_idle[self.weapon]

        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.img, self.rot + 90)
        self.rect = self.image.get_rect()
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos

        #wall collission
        self.hit_rect.centerx = self.pos.x
        collision_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collision_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        #car collossion
        if not self.inside_vehicle:
            self.hit_rect.centerx = self.pos.x
            collision_cars(self, self.game.cars, 'x')
            self.hit_rect.centery = self.pos.y
            collision_cars(self, self.game.cars, 'y')
            self.rect.center = self.hit_rect.center


        self.mask = pg.mask.from_surface(self.image)

        if self.inside_vehicle :
            self.pos = self.game.car.pos
            self.rot = self.game.car.rot
            self.image.fill((255, 255, 0, 0))

        point = vec(100,0) - BARREL_OFFSET
        self.point = point.rotate(-self.rot)
        self.pointer = self.pos - self.point


    def attack(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            random.choice(self.game.swoosh).play()
            hits = pg.sprite.spritecollide(self,self.game.enemies,False,collide_hit_rect2)
            if hits:
                self.game.splash_sound.play()

                hits[0].health -= 20
        self.attacking = True


class Walls(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = ENEMY_LAYER
        self.groups = game.enemies, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.enemy_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = ENEMY_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.acc = vec(0, 0)
        self.vel = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 270
        self.health = 100
        self.last_shot = 0
        self.bullet_rate = {'pistol' : random.randint(1000, 1500),
                            'pistol_loud': random.randint(1000, 1500),
                            'shotgun': random.randint(1500, 2500)}
        self.spread = random.randint(2, 5)
        self.target = self.game.player
        self.dir = vec(0,1)
        self.weapon = random.choice(['pistol_loud','shotgun','pistol_loud'])
        self.type = 'enemy'
        self.barrel_offset = ENEMY_BARREL_OFFSET

    def show_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / 100)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < ENEMY_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)

    def fire(self):
        pass

    def avoid_other(self):
        for enemy in self.game.enemies:
            if enemy != self:
                dist = self.pos - enemy.pos
                if 0 < dist.length() < 50:
                    self.acc += dist.normalize()

    def update(self):
        flag = False
        target_dis = self.game.player.pos - self.pos
        if target_dis.length_squared() < DETECT_RADIUS ** 2:
            flag = True
            self.rot = target_dis.angle_to(vec(0, -1))
            self.image = pg.transform.rotate(self.game.enemy_img, self.rot + 180)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(0, -1).rotate(-self.rot)
            self.avoid_other()
            self.acc.scale_to_length(ENEMY_SPEED)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + .5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collision_walls(self, self.game.walls, 'x')
            self.hit_rect.center = self.pos
            collision_walls(self, self.game.walls, 'y')
            self.hit_rect.center = self.rect.center
            length = hypot(self.game.player.pos.x - self.pos.x, self.game.player.pos.y - self.pos.y)
            if length < 150:
                self.acc = vec(0, ENEMY_SPEED).rotate(-self.rot)
                self.vel = self.acc * self.game.dt
        if self.health <= 0:
            self.kill()
            self.game.splat_sound.play()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))

        self.mask = pg.mask.from_surface(self.image)

        now = pg.time.get_ticks()
        if now - self.last_shot > self.bullet_rate[self.weapon] and flag:
            shoot(self)
            self.last_shot = now


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir,user,damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites , game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.user = user
        self.image = self.game.bullet_images[WEAPONS[user.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        # spread = uniform(-BULLET_SPREAD, BULLET_SPREAD)
        self.vel = dir * -WEAPONS[user.weapon]['bullet_speed'] *uniform(.9,1.1)
        self.hit_rect = self.rect
        self.spawn_time = pg.time.get_ticks()
        angle = vec(0, 1).angle_to(dir)
        self.image = pg.transform.rotate(self.image, -angle)
        self.damage = damage
    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if self.user.weapon != 'fist':
            if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.user.weapon]['lifetime']:
                self.kill()
        hits = pg.sprite.spritecollide(self, self.game.walls, False)
        if hits:
            self.kill()


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y



class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = random.randint(20, 50)
        self.image = pg.transform.scale(random.choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1


class Cars(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.group = game.all_sprites, game.cars
        pg.sprite.Sprite.__init__(self, self.group)
        self.game = game
        self.image = game.car_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.hit_rect = CAR_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.empty = True
        self.rot = 270
        self.rot_speed = CAR_ROT_SPEED
        self.speed = CAR_SPEED
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.friction = CAR_FRICTION
        self.time = 0

    def update(self):

        if self.empty == False and self.game.player.inside_vehicle == True:
            self.move()
            self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
            self.image = pg.transform.rotate(self.game.car_img, self.rot + 90)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos

            self.hit_rect.centerx = self.pos.x
            collision_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collision_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
            self.acc += self.vel * CAR_FRICTION
            self.vel += self.acc * self.game.dt

            self.pos += self.vel + .5 * self.acc * self.game.dt ** 2
            self.mask = pg.mask.from_surface(self.image)

    def stop(self):
        self.acc = vec(0,0)
    def move(self):
        self.rot_speed = 0
        self.acc = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.rot_speed = CAR_ROT_SPEED
            self.acc = -vec(CAR_SPEED / 5, 0).rotate(-self.rot)
        if keys[pg.K_d]:
            self.rot_speed = - CAR_ROT_SPEED
            self.acc = -vec(CAR_SPEED / 5, 0).rotate(-self.rot)
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.acc = - vec(CAR_SPEED, 0).rotate(-self.rot)

        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.acc = vec(CAR_SPEED / 2, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            self.acc = vec(-self.vel, 0)


class Crosshair(pg.sprite.Sprite):
    def __init__(self, game, pos ):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((5,5))
        self.image.fill((255,0,0,255))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = pos
        self.hit_rect = self.rect

    def update(self):
        self.pos = self.game.player.pointer
        self.rect.center = self.pos
        if self.game.player.weapon == 'fist':
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)