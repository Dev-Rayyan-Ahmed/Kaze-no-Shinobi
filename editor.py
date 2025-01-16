import pygame
import sys
from icecream import ic
from scripts.utils import load_image,load_images
from scripts.tilemap import Tilemap

RENDER_SCALE = 2.0

class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Editor')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240)) # .Surface() loads an empty image of (320,240) dimension,
                                                  # which is all Black

        #The idea is to render on self.display (smaller than screen) and scale it to self.screen
        # to create a pixel like effect

        self.clock = pygame.time.Clock()  # to run game on 60 fps

        #Defining Assets as Dictionary, so that we can access image with custom key
        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "spawners": load_images("tiles/spawners"),
            "stone": load_images("tiles/stone"),
        }

        self.movement = [False, False,False,False] # for Camera Movement

        self.tilemap = Tilemap(self,tile_size=16)

        try:
            #LOAD FUNCTION
            self.tilemap.load("1.json")
        except FileNotFoundError:
            pass

        self.scroll = [0,0] #camera's location , which is added to each rendering

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False

        self.ongrid = True

    def run(self):
        while True:
            self.display.fill((0,0,0))

            #Camera Movement:
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2 # control X-axis
            self.scroll[1] += (self.movement[3] - self.movement[2]) *2  # control Y-Axis

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.tilemap.render(self.display,render_scroll)


            # on first run selects the first time of first group
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()

            #for partially transparent
            current_tile_img.set_alpha(100)

            mpos = pygame.mouse.get_pos() #returns the position of mouse with respect to you window's screen
            # so it's the display pos not the Screen, therefore we need to
            #because our each pixel is 2 pixel
            mpos = (mpos[0]/RENDER_SCALE, mpos[1]/RENDER_SCALE)


            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size),int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))


            if self.ongrid:
            #to know where are we placing
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1]* self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)


            #placing tile
            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ";" + str(tile_pos[1])] = {"type": self.tile_list[self.tile_group],"variant": self.tile_variant,"pos":tile_pos}

            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ";" + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap: # Means tile exist at that pos or loc
                    del self.tilemap.tilemap[tile_loc]

                # for offGrid
                for tile in self.tilemap.offgrid_tiles.copy():
                   #tile is a dictionary with keys type,variant,pos
                   #while offgrid_tiles is a list of these dictionaries

                    tile_img = self.assets[tile["type"]][tile["variant"]]

                    #position of tile_img
                    tile_r = pygame.Rect(tile["pos"][0] - self.scroll[0], tile["pos"][1] - self.scroll[1], tile_img.get_width(),tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)



            self.display.blit(current_tile_img, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({"type": self.tile_list[self.tile_group],"variant": self.tile_variant,"pos":(mpos[0] + self.scroll[0],mpos[1]+ self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking= True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]]) # % for looping
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list) # % for looping
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0


                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False


                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.auto_tile()
                    if event.key == pygame.K_o:
                        self.tilemap.save("1.json")

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            #bliting self.display on the self.screen
            #pygame.transform.scale(<which surface to scale>,<New Size>)
            # a.get_size() return the size of surface a
            self.screen.blit(pygame.transform.scale(self.display,self.screen.get_size()),(0,0))
            pygame.display.update()
            self.clock.tick(60)  # to run our code at 60 fps

Editor().run()
