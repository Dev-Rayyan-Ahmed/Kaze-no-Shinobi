import json
import pygame


#can't use list as key, but can use tuple
# if <these are neighbours> : <use this variant>
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}


NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {"grass", "stone"}  # Set for efficient searching, since duplicates are not allowed
AUTOTILE_TYPES = ["grass","stone"]

class Tilemap:
    def __init__(self, game, tile_size=16):  # 16 is default value
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

        # {"0;1" : "grass" , "9999;0" ; "dirt"}

        # for i in range(10):
        #     # storing titles in tilemap
        #     # <Location of Tile>   = <representing tile as dictionary>
        #
        #     # Horizontal Line
        #     self.tilemap[str(3 + i) + ";10"] = {"type": "grass", "variant": 1, "pos": (3 + i, 10)}
        #
        #     # Vertical Line
        #     self.tilemap["10;" + str(5 + i)] = {"type": "stone", "variant": 1, "pos": (10, 5 + i)}


    def solid_check(self,pos):
        #changing pixel to grid
        tile_loc = str(int(pos[0]//self.tile_size)) + ";" + str(int(pos[1]//self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]["type"] in PHYSICS_TILES:
                return self.tilemap[tile_loc]


    def extract(self,id_pairs,keep=False):
        #id_pairs = list of id(s) we want to work on, i.e: [(type,variant),(more)]
        matches = []
        for tile in self.offgrid_tiles.copy():
            if(tile["type"],tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if(tile["type"],tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                matches[-1]["pos"] = matches[-1]["pos"].copy()
                #changing it to pixel value

                matches[-1]["pos"][0] *= self.tile_size
                matches[-1]["pos"][1] *= self.tile_size

                if not keep:
                    del self.tilemap[loc]

        return matches



    def tile_around(self, pos):  # Generating tiles around the pos
        tiles = []

        # tile_loc contain pos value in grid, while pos has pixel value
        #        = <changes pixel position to grid position>
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ";" + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])  # append all the tiles around the pos location
        return tiles

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tile_around(pos):
            if tile["type"] in PHYSICS_TILES:
                # since tiles are squares, their height and widths == self.tile_size
                rects.append(
                    pygame.Rect(tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size, self.tile_size,
                                self.tile_size))
        return rects

    def auto_tile(self):
        for loc in self.tilemap: # keys are location of tiles
            tile = self.tilemap[loc]
            neighbours = set()
            for shift in [(1,0),(-1,0),(0,1),(0,-1)]:
                check_loc = str(tile["pos"][0]+ shift[0]) + ";" + str(tile["pos"][1] + shift[1]) #checking surrounding tiles
                if check_loc in self.tilemap:
                    #checking if neighbouring tiles are the same type
                    if self.tilemap[check_loc]["type"] == tile["type"]:
                        neighbours.add(shift)
            neighbours = tuple(sorted(neighbours))
            if (tile["type"] in AUTOTILE_TYPES) and (neighbours in AUTOTILE_MAP):
                tile["variant"] = AUTOTILE_MAP[neighbours]

    def save(self,path):
        f = open(path, "w")
        json.dump({"tilemap":self.tilemap, "tile_size": self.tile_size, "offgrid":self.offgrid_tiles},f)
        f.close()

    def load(self,path):
        f = open(path, "r")
        map_data = json.load(f)
        f.close()
        self.tilemap = map_data["tilemap"]
        self.tile_size = map_data["tile_size"]
        self.offgrid_tiles = map_data["offgrid"]


    def render(self, surf, offset=(0, 0)):


        # rendering off_grid first, because they are ofter decorations while grid ones are used as
        # platforms, where player can move and collide

        # whene rendering off_grid_tiles we don't * by tile_size, because we are keeping them as pixels
        # and not as grid position

        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile["type"]][tile["variant"]],
                      (tile["pos"][0] - offset[0], tile["pos"][1] - offset[1]))

            # subtracting as when we move to left,
            # everything else moves to right

        # [3] Copy notes
        # loc = location
        for x in range(offset[0]//self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ";" + str(y)
                if loc in self.tilemap: #by default iterate over keys
                    tile = self.tilemap[loc]
                    #Explained in [2] copt notes
                    surf.blit(self.game.assets[tile["type"]][tile["variant"]],
                                  (tile["pos"][0] * self.tile_size - offset[0], tile["pos"][1] * self.tile_size - offset[1]))

