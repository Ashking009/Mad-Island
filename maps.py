import pygame as pg
import pytmx
from settings import *

def collide_hit_rect(one,two):
    return one.hit_rect.colliderect(two.rect)

def collide_hit_rect2(one,two):
    return one.hit_rect.colliderect(two.hit_rect)

class Map:
    def __init__(self,filename):
        self.map_data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.map_data.append(line.strip())

        self.tilewidth = len(self.map_data[0])
        self.tileheight = len(self.map_data)
        self.width =  self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

class Tilemap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename,pixelalfa = True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata =tm
    def show(self,surf):
        tile_img =self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = tile_img(gid)
                    if tile:
                        surf.blit(tile,(x * self.tmxdata.tilewidth,y *self.tmxdata.tileheight))

    def make_map(self):
        loc_surf = pg.Surface((self.width,self.height))
        self.show(loc_surf)
        return loc_surf

class Camera:
    def __init__(self,width,height):
        self.camera = pg.Rect(0,0,width,height)
        self.width = width
        self.height = height

    def apply(self,entity):
        return entity.rect.move(self.camera.topleft)
    def apply_rect(self,rect):
        return rect.move(self.camera.topleft)

    def update(self,target):
        x = -target.rect.centerx + int(WIDTH/2)
        y = -target.rect.centery + int(HEIGHT/2)

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH),x)
        y = max(-(self.height - HEIGHT), y)
        self.camera = pg.Rect(x,y,self.width,self.height)