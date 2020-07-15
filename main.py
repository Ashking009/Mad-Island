import pygame as pg
from settings import *
from sprites import *
import random
from maps import *
from os import path
# from pygame import mixer
import sys
#HUD

def show_player_health(surface, x , y, per):
    if per < 0:
        per =0
    BAR_LEN = 100
    BAR_HEI = 20
    fill = per * BAR_LEN
    outer_rect = pg.Rect(x,y,BAR_LEN,BAR_HEI)
    inner_rect = pg.Rect(x,y,fill,BAR_HEI)
    if per > .6:
        col = GREEN
    elif per > .3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surface , col, inner_rect)
    pg.draw.rect(surface, WHITE, outer_rect,2)

def show_player_weapon(surface,x,y):
    pass



class Game:
    def __init__(self):
        pg.mixer.pre_init(22050,-16,2,1024)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.game_over = True
        self.font_name =pg.font.match_font(FONT_NAME)
        self.load_data()
        self.x = 0

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder,'img')
        sound_folder = path.join(game_folder,'sound')
        self.map_folder = path.join(game_folder,'maps')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0,0,0,180))
        self.enemy_img = pg.image.load(path.join(img_folder, ENEMY_IMAGE)).convert_alpha()
        self.car_img = pg.image.load(path.join(img_folder, CAR_IMAGE)).convert_alpha()
        self.player_imgs = {}
        for img in PLAYER_IMAGES:
            self.player_imgs[img] = pg.image.load(path.join(img_folder,PLAYER_IMAGES[img])).convert_alpha()
        self.player_idle ={'pistol':self.player_imgs['idle_weap'],
                           'shotgun':self.player_imgs['idle_weap'],
                           'assault_rifle':self.player_imgs['idle_weap'],
                           'fist':self.player_imgs['fist_idle']}

        self.bullet_images = {}
        self.bullet_images['large'] = pg.image.load(path.join(img_folder, BULLET_IMAGE)).convert_alpha()

        self.bullet_images['small'] = pg.transform.scale(self.bullet_images['large'],(7,7)).convert_alpha()
        self.bullet_images['large'] = pg.transform.scale(self.bullet_images['large'],(12,12)).convert_alpha()
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat =pg.transform.scale(self.splat,(64,64))
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
        pg.mixer.music.load(path.join(sound_folder ,GAME_MUSIC))
        pg.mixer.music.set_volume(0.08)

        self.gunshot = pg.mixer.Sound(path.join(sound_folder,GUN_SOUND))
        self.gunshot.set_volume(.2)
        self.car_start = pg.mixer.Sound(path.join(sound_folder,CAR_START))
        self.car_start.set_volume(0.2)
        self.engine = pg.mixer.Sound(path.join(sound_folder,CAR_ENGINE))
        self.engine.set_volume(.2)
        self.engine_stop = pg.mixer.Sound(path.join(sound_folder,CAR_STOP))
        self.splat_sound = pg.mixer.Sound(path.join(sound_folder,SPLAT_SOUND))
        self.splat_sound.set_volume(.2)
        self.splash_sound = pg.mixer.Sound(path.join(sound_folder,SPLASH_SOUND))
        self.splash_sound.set_volume(.2)
        self.switch = pg.mixer.Sound(path.join(sound_folder,SWITCH_SOUND))
        self.switch.set_volume(.4)
        self.denied = pg.mixer.Sound(path.join(sound_folder,DENIED_SOUND))
        self.denied.set_volume(.1)
        self.swoosh = []
        for item in SWOOSH_SOUNDS:
            s= pg.mixer.Sound(path.join(sound_folder,item))
            self.swoosh.append(s)
        self.effect_sound = {}
        for item in ITEM_SOUND:
            self.effect_sound[item] = pg.mixer.Sound(path.join(sound_folder,ITEM_SOUND[item]))
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUND:
            self.weapon_sounds[weapon]=[]
            for sound in WEAPON_SOUND[weapon]:
                s =pg.mixer.Sound(path.join(sound_folder,sound))
                s.set_volume(.3)
                self.weapon_sounds[weapon].append(s)


    def new(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.enemies = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.cars = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.player_bullets = pg.sprite.Group()
        self.map = Tilemap(path.join(self.map_folder, 'mainmap.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.x = 0

        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width/2 ,tile_object.y +tile_object.height /2)
            if tile_object.name =='player':
                self.player = Player(self,obj_center.x,obj_center.y)
                self.crosshair = Crosshair(self,self.player.pos)
            if tile_object.name =='wall':
                Obstacle(self,tile_object.x,tile_object.y,tile_object.width,tile_object.height)
            if tile_object.name =='enemy':
                Enemy(self,obj_center.x,obj_center.y)
            if tile_object.name in ['health','shotgun','assault_rifle','pistol']:
                Item(self, obj_center, tile_object.name)
            if tile_object.name == 'car':
                Cars(self,obj_center.x,obj_center.y)
        self.draw_debug = False

        self.camera = Camera(self.map.width,self.map.height)
        self.paused = False


    def run(self):
        self.playing =True
        if not self.paused: 
            pg.mixer.music.play(-1)
        while self.playing :

            self.dt = self.clock.tick(FPS) /1000

            self.event()
            if not self.paused:
                self.update()
            self.draw()

    def grid(self):
        for i in range(0,WIDTH,TILESIZE):
            pg.draw.line(self.screen,WHITE,(i,0),(i,HEIGHT))
        for j in range(0,HEIGHT,TILESIZE):
            pg.draw.line(self.screen,WHITE,(0,j),(WIDTH,j))

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
                self.game_over = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    hi = pg.sprite.spritecollide(self.player, self.cars, False,pg.sprite.collide_mask)
                    if hi:
                        self.car = hi[0]
                        if not self.player.inside_vehicle:

                            self.player.rot = self.car.rot
                            self.player.inside_vehicle = True
                            self.car.empty = False
                            self.car_start.play()
                            self.engine.play(-1)
                            self.all_sprites.remove(self.crosshair)

                        elif self.player.inside_vehicle:
                            self.car.empty = True
                            self.player.inside_vehicle = False
                            self.engine.stop()
                            self.engine_stop.play()
                            dir = vec(0,40).rotate(-self.car.rot)
                            new_pos = self.car.pos - dir
                            self.player.pos = new_pos
                            self.all_sprites.add(self.crosshair)

                if event.key == pg.K_p:
                    self.paused = not self.paused
                # if event.key ==pg.K_h:
                #     self.draw_debug = not self.draw_debug

                if event.key == pg.K_q:
                    if len(self.player.weapon_list) > 1:
                        self.switch.play()
                        self.x += 1
                        self.player.weapon = self.player.weapon_list[self.x % len(self.player.weapon_list)]
                        if self.x % len(self.player.weapon_list) == 0:
                            self.x = 0
                    else:
                        self.denied.play()

    def update(self):
        self.all_sprites.update()
        if not len(self.enemies):
            self.playing = False
        self.camera.update(self.player)
        hits = pg.sprite.groupcollide(self.enemies,self.player_bullets,False,True)
        for enemy in hits:
            for bullet in hits[enemy]:
                enemy.health -= bullet.damage

        hits_e = pg.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if hits_e:
            no_of_bullets = len(hits_e)
            if no_of_bullets == 1:
                damage = 10
            else:
                damage = 5
            self.player.health -= damage * no_of_bullets
        if not self.player.inside_vehicle:
            hits = pg.sprite.spritecollide(self.player, self.items, False)
            for hit in hits:
                if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                    hit.kill()
                    self.effect_sound['health'].play()
                    self.player.add_health(HEALTH_PACK_AMOUNT)
                if hit.type =='pistol':
                    hit.kill()
                    self.effect_sound['shotgun'].play()
                    if hit.type not in self.player.weapon_list:
                        self.player.weapon_list.append(hit.type)
                    self.player.weapon = 'pistol'
                    self.x += 1
                if hit.type =='shotgun':
                    hit.kill()
                    self.effect_sound['shotgun'].play()
                    if hit.type not in self.player.weapon_list:
                        self.player.weapon_list.append(hit.type)
                    self.player.weapon = 'shotgun'
                    self.x += 1
                if hit.type =='assault_rifle':
                    hit.kill()
                    self.effect_sound['shotgun'].play()
                    if hit.type not in self.player.weapon_list:
                        self.player.weapon_list.append(hit.type)
                    self.player.weapon = 'assault_rifle'
                    self.x += 1


        hits= pg.sprite.groupcollide(self.enemies,self.cars,False,False,pg.sprite.collide_mask)
        for hit in hits:
            if hits[hit][0].vel.length()> 5:
                self.splash_sound.play()
                hit.pos += hit.dir * 20
                time = pg.time.get_ticks()
                if time>500:
                    hit.health = 0

        hits = pg.sprite.groupcollide(self.bullets,self.cars,False,False,collide_hit_rect2)
        for hit in hits:
            hit.kill()



    def draw(self):
        self.screen.blit(self.map_img,self.camera.apply_rect(self.map_rect))
        # pg.display.set_caption("{: .2f}".format(self.clock.get_fps()))
        for sprite in self.all_sprites:
            if isinstance(sprite,Enemy):
                sprite.show_health()
            self.screen.blit(sprite.image , self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen,YELLOW,self.camera.apply_rect((sprite.hit_rect)),2)
                for wall in self.walls:
                    pg.draw.rect(self.screen,YELLOW,self.camera.apply_rect((wall.rect)),2)
        self.screen.blit(self.item_images[self.player.weapon], (200,35))
        self.draw_text('Health', 32, WHITE, 60,20)
        self.draw_text('Weapon', 20, YELLOW, 220,20)
        show_player_health(self.screen, 10, 40, self.player.health/ PLAYER_HEALTH )
        self.draw_text('Enemies left : ' + str(len(self.enemies)),32,WHITE,WIDTH -120 , 20)

        if self.paused:
            self.screen.blit(self.dim_screen,(0,0))
            self.draw_text('PAUSED',105,RED,WIDTH/2,HEIGHT/2)

        pg.display.flip()

    def show_start_screen(self):
        self.playing = False

    def draw_text(self,text,size,color,x,y):
        font =pg.font.Font(self.font_name,size)
        text_surface = font.render(text,True,color)
        text_rect = text_surface.get_rect()
        text_rect.center =(x,y)
        self.screen.blit(text_surface,text_rect)

    def go(self):
        if self.game_over:
            self.screen.fill(BLACK)
            self.draw_text("GAME OVER",100,WHITE,WIDTH/2,HEIGHT/2)
            self.draw_text("Press any key to start again",30,RED,WIDTH/2 ,HEIGHT/2 +50)
            pg.display.flip()
            self.wait_key()
    def wait_key(self):
        pg.event.wait()
        while self.game_over:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game_over = False
                    self.running = False

                    pg.quit()
                if event.type == pg.KEYUP:
                    self.game_over = False
        

g= Game()
g.show_start_screen()
while g.running:
    g.new()
    g.run()
    g.go()

pg.quit()
