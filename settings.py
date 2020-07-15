import pygame as pg

vec = pg.math.Vector2
import random

WIDTH = 1024
HEIGHT = 768
TITLE = "Mad Island"
FPS = 60
FONT_NAME = 'arial'
TILESIZE = 64
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (116, 56, 0)

# player ppties
PLAYER_SPEED = 250
PLAYER_ROT_SPEED = 200
PLAYER_IMAGE = 'hitman.png'
PLAYER_IMAGE_IDLE = 'hitman_idle.png'
PLAYER_NO_WEAP = 'player_no_weap.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 33, 33)
PLAYER_HEALTH = 100
PLAYER_IMAGES = {'fist_idle':'idle_no_weap.png',
                 'fist':'fist_attack.png',
                 'idle_weap': 'idle_weap.png',
                 'pistol': 'shoot_pistol.png',
                 'shotgun': 'shoot_shotgun.png',
                 'assault_rifle':'shoot_assault.png'}

ENEMY_IMAGE = 'survivor1_machine.png'
ENEMY_SPEED = 150
ENEMY_HIT_RECT = pg.Rect(0, 0, 30, 30)
ENEMY_HEALTH = 100
ENEMY_BARREL_OFFSET = vec(9, -30)
AVOID_RAD = 50
SPLAT = 'splat_red.png'

MUZZLE_FLASHES = ['whitePuff1.png', 'whitePuff2.png', 'whitePuff3.png',
                  'whitePuff4.png']
FLASH_DURATION = 40

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
ENEMY_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1
DETECT_RADIUS = 500

BULLET_IMAGE = 'bullet.png'
BARREL_OFFSET = vec(-30, -10)


ITEM_IMAGES = {'health': 'health_pack.png',
               'fist':'fist.png',
               'pistol':'pistol.png',
               'shotgun':'shotgun.png',
               'assault_rifle':'assault_rifle.png'}
HEALTH_PACK_AMOUNT = 30
BOB_RANGE = 15
BOB_SPEED = 0.4
CAR_IMAGE = 'top-down-car-big.png'
CAR_HIT_RECT = pg.Rect(0, 0, 56, 60)
CAR_ROT = 80
CAR_ROT_SPEED = 150
CAR_SPEED = 18
CAR_FRICTION = -3

GUN_SOUND = 'gunshot_loud.wav'
# GUN_SILENCED = 'gunshot_silenced.wav'
CAR_START = 'car_starts.wav'
CAR_ENGINE = 'engine_run.wav'
# CAR_ENGINE = 'car_engine.wav'
CAR_STOP = 'engine_stops.wav'
CAR_RACE = 'engine_race.wav'
SPLAT_SOUND = 'splat.wav'
SPLASH_SOUND = 'splash.wav'
ITEM_SOUND = {'health':'health.wav',
              'shotgun': 'weapon_pick.wav',
              'assault_rifle':'weapon_pick.wav'}

GAME_MUSIC = 'back.mp3'

WEAPONS = {}
WEAPONS['fist'] = dict(damage = 30, rate = 500)
WEAPONS['pistol'] = dict(bullet_speed=600, lifetime=500,
                         rate=250, kickback=-50, damage=10, spread=2,
                         bullet_size='large', bullet_count=1)
WEAPONS['pistol_loud'] = dict(bullet_speed=600, lifetime=500,
                         rate=250, kickback=-50, damage=10, spread=2,
                         bullet_size='large', bullet_count=1)
WEAPONS['shotgun'] = dict(bullet_speed=400, lifetime=400,
                         rate=1100, kickback=-150, damage=10, spread=20,
                         bullet_size='small', bullet_count=12)
WEAPONS['assault_rifle'] = dict(bullet_speed=800, lifetime=500,
                         rate=150, kickback=-100, damage=10, spread=3,
                         bullet_size='large', bullet_count=1)

WEAPON_SOUND = {'pistol': ['pistol.wav'],
                'shotgun': ['shotgun.wav'],
                'assault_rifle':['assault_rifle.wav'],
                'pistol_loud':['gunshot_loud.wav']}

SWITCH_SOUND = 'switch_weap.wav'
DENIED_SOUND = 'den_short.wav'

SWOOSH_SOUNDS = ['swoosh1.wav','swoosh2.wav','swoosh3.wav']


