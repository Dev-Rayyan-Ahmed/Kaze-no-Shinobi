import pygame
import sys
import random
import math
import os

from scripts.utils import load_image,load_images,Animation
from scripts.entities import Player,Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark

class Game:
    def __init__(self):

        pygame.init()

        #Icon
        icon = pygame.image.load("data/icon.png")
        pygame.display.set_icon(icon)

        #Display 1 for those that need outline
        #Display 2 for the upper layer / no outline effect

        pygame.display.set_caption('Kaze no Shinobi')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240),pygame.SRCALPHA) # .Surface() loads an empty image of (320,240) dimension,
                                                  # which is all Black
        self.display_2 = pygame.Surface((320, 240))

        #The idea is to render on self.display (smaller than screen) and scale it to self.screen
        # to create a pixel like effect

        self.clock = pygame.time.Clock()  # to run game on 60 fps

        self.movement = [False, False]

        #Defining Assets as Dictionary, so that we can access image with custom key

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            # "spawners": load_images("tiles/spawners"),
            "stone": load_images("tiles/stone"),

            "player": load_image("entities/player.png"),

            "background": load_image("background.png"),

            "background2": load_image("background3.png"),

            "clouds": load_images("clouds"),

            "enemy/idle" : Animation(load_images("entities/enemy/idle"),img_dur=6,loop=True),
            "enemy/run" : Animation(load_images("entities/enemy/run"),img_dur=4,loop=True),

            "player/idle" : Animation(load_images("entities/player/idle"),img_dur=6,loop = True),
            "player/run": Animation(load_images("entities/player/run"), img_dur=4, loop=True),
            "player/jump": Animation(load_images("entities/player/jump"), img_dur=5, loop=True),
            "player/slide": Animation(load_images("entities/player/slide"), img_dur=5, loop=True),
            "player/wall_slide": Animation(load_images("entities/player/wall_slide"), img_dur=5, loop=True),
            "particle/leaf" : Animation(load_images("particles/leaf"), img_dur=20, loop=False),
            "particle/particle": Animation(load_images("particles/particle"), img_dur=6, loop=False),

            "gun" : load_image("gun.png"),
            "projectile": load_image("projectile.png"),
        }

        self.sfx = {
            "jump" : pygame.mixer.Sound('data/sfx/jump.wav'),
            "dash": pygame.mixer.Sound('data/sfx/dash.wav'),
            "hit": pygame.mixer.Sound('data/sfx/hit.wav'),
            "shoot": pygame.mixer.Sound('data/sfx/shoot.wav'),
            "ambience": pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        #Setting Volume
        self.sfx["ambience"].set_volume(0.2)
        self.sfx["jump"].set_volume(0.7)
        self.sfx["dash"].set_volume(0.3)
        self.sfx["hit"].set_volume(0.8)
        self.sfx["shoot"].set_volume(0.4)


        self.clouds = Clouds(self.assets["clouds"],count = 16)

        self.player = Player(self,(50,50),(8,15))
        #self is passed as argument in the place of game, so that it can have access to this class

        self.tilemap = Tilemap(self,tile_size=16)
        self.level = 0
        self.load_level(self.level)

        self.screenshake = 0

        self.font = pygame.font.Font("Roboto-Regular.ttf", 30)
        self.text_color = (255, 255, 255)  # White

        self.credits = [
            "Game Developed By:",
            "Rayyan Ahmed",
            "",
            "Design and Animation:",
            "Rayyan Ahmed",
            "",

            "Spirit Design:",
            "Rayyan Ahmed",
            "",

            "Map layout",
            "Rayyan Ahmed",
            "",

            "Programming Language:",
            "Python",
            "",
            "Main Library Used:",
            "Pygame",
            "",
            "Other Libraries Used:",
            "Math,Random,Os,Sys",
            "",

            "Game Packaging by",
            "PyInstaller",
            "",

            "In-Music:",
            "Credit Song for My Death",
            "",
            "Credits Music:",
            "Death Rattle",
            "",
            "Game Testing:",
            "Muhammad Kashan",
            "",
            "Game Version:",
            "Version 1.0.0",
            "",
            "Game Inspiration:",
            "Hollow Knight",
            "",
            "This project was created as part of an",
            "Object-Oriented Programming (OOP) project.",
            "",
            "Thank You for Playing!",

            "Kaze = Wind (In Japaneses)",
            "Kaze No Shinobi = Shinobi of the Wind",
            "",

            "All Musics",
            "Belong to their Original Owners",
            "",
        ]

    def load_level(self,map_id):
        self.tilemap.load("data/maps/" + str(map_id) + ".json")

        self.leaf_spawner = []
        for tree in self.tilemap.extract([("large_decor",2),],keep=True):
            #Collecting Locations to Spawn leaves and Off_set by 4
            self.leaf_spawner.append(pygame.Rect(4+tree["pos"][0],4+tree["pos"][1],23,13))


        self.enemies = []
        for spawner in self.tilemap.extract([("spawners",0),("spawners",1)],keep=False):
            #keep = False to replace spawners with entities
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self,"enemy",pos=spawner["pos"],size =(8,15)))

        self.projectiles = []
        self.particles=[]
        self.sparks = [] #amazing stuff

        self.scroll = [0,0] #camera's location , which is added to each rendering

        self.dead = 0
        self.transition = -30

    def credit(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load("data/Credits.wav")
        pygame.mixer.music.play(-1)

        scroll_y = 600  # Start position for scrolling
        running = True

        # Draw the background
        img = pygame.image.load("data/Credit_BG.jpg")


        self.transition2 = -30
        x = 1
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Exit credits on ESC
                        pygame.quit()
                        running = False

            if (not len(self.enemies)) and True:
                self.transition2 = min(0,self.transition2+ 1)
                if self.transition2 <= 0:
                    scaled_surface = pygame.transform.scale(img, (640, 480))
                    self.screen.blit(scaled_surface, (0, 0))

                    # if x == 1:
                    #     self.transition2 = -30
                    #     x+=1

            if self.transition2 <0:
                self.transition2 = min(0, self.transition2 + 1)

            if self.transition2:
                transition2_surf = pygame.Surface((self.screen.get_size()))
                pygame.draw.circle(transition2_surf, (255, 255, 255),
                                   (self.screen.get_width() // 2, self.screen.get_height() // 2),
                                   ((35 - abs(self.transition2)) * 16))
                transition2_surf.set_colorkey((255, 255, 255))
                self.screen.blit(transition2_surf, (0, 0))


            # Render and display credits
            y_offset = scroll_y
            for line in self.credits:
                text_surface = self.font.render(line, True, self.text_color)
                text_rect = text_surface.get_rect(center=(325, y_offset))
                self.screen.blit(text_surface, text_rect)
                y_offset += 50  # Space between lines

            # Scroll the credits
            scroll_y -= 2
            if scroll_y < -len(self.credits) * 50:  # Reset scrolling after the last line
                scroll_y = 600

            pygame.display.flip()
            pygame.time.Clock().tick(60)


    def run(self):
        pygame.mixer.music.load("data/music.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx["ambience"].play(-1)

        while True:

            self.display.fill((0,0,0,0)) #Pure Transparency
            if not (self.level == 2):
                self.display_2.blit(self.assets["background"],(0,0))
            elif self.level == 2:
                self.display_2.blit(self.assets["background2"],(0,0))

            self.screenshake = max(0,self.screenshake-1)

            if not len(self.enemies):
                self.transition +=1
                if self.transition > 30:
                    self.level +=1
                    if self.level > 2:
                        self.credit()
                    self.level = min(self.level, len(os.listdir("data/maps")) -1 )
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition +=1

            if self.dead:
                self.dead +=1
                if self.dead >= 10:
                    self.transition = min(30,self.transition+1) #to avoid lvl count
                if self.dead > 40: #Timer
                    self.load_level(self.level) # Reset map

            #for smooth camera movement, we find how far away camera is from where we want it to be and then added it to self.scroll
            #                <returns player current center value> - <Display center value> - <current scroll value>
            #                              <how far is player from center> - <current camera value>
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0])/30
            #                                                   Divide by 30, so that the further is player the faster camera moves

            #same for y-axis
            self.scroll[1] += (self.player.rect().centery - self.display.get_height()/2 - self.scroll[1])/30

            # rn, the value of scroll are floats, so turning them to int for smooth experience (whole numbers)
            # also, it restricts Sub-pixel movements
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            #Spawing Leafs
            for rect in self.leaf_spawner:
                if random.random()*49999 < rect.width * rect.height: #to make it not spawn every frame
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, "leaf", pos,velocity=[-0.1,0.3],frame=random.randint(0,20)))
                    # random.randint(), so that it can have a random frame everytime


            #update and render the clouds
            if not (self.level == 2):
                self.clouds.update()
                self.clouds.render(self.display_2,offset=render_scroll)

            #render the tiles + also adding offset ie how much we are moving when rendering
            self.tilemap.render(self.display, offset = render_scroll)

            #Redering the enemies
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap,(0,0))
                enemy.render(self.display,offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)


            if not self.dead:
                #updating PlayerMovement Each Iteration, by using method .update defined in PhysicsEntity
                self.player.update(self.tilemap,(self.movement[1]-self.movement[0],0)) #the (,0) in movement
                                                                          # represent that we don't want movement in y-axis

                #Rendering Player Using .render method defined in PhysicsEntity
                self.player.render(self.display, offset = render_scroll )

            #rendering and managing Projectiles.
            # each projectile in [ [x,y] , direction, time ]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1] # x += direction
                projectile[2] += 1 # time increment
                img = self.assets["projectile"]
                self.display.blit(img,(projectile[0][0] - img.get_width()/2 - render_scroll[0],projectile[0][1] - img.get_height()/2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]): #checking if it hit some solid area
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(
                            Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))

                elif projectile[2] >360: #timer > 360
                    self.projectiles.remove(projectile)
                elif self.player.dashing < 50: #while not dashing/in cooldown
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead +=1
                        self.sfx["hit"].play()
                        self.screenshake = max(16,self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center,angle, 2 + random.random()))
                            self.particles.append(Particle(self, "particle", self.player.rect().center,velocity=[math.cos(angle + math.pi) * speed * 0.5,math.sin(angle + math.pi) * speed * 0.5],frame=random.randint(0,7)))

            #Sparks
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display,offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            #Outline
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))

            for offset in [(-1,0),(1,0),(0,-1),(0,1)]:
                self.display_2.blit(display_sillhouette,offset)

            #Remove particle when it's animation ends
            for particle in self.particles:
                kill = particle.update()
                particle.render(self.display, offset = render_scroll)
                if particle.type == "leaf":
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx["jump"].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_m:
                        self.credit()
                    if event.key == pygame.K_n:
                        self.level+=1

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            #Transition:
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size()) #Creats a surface to blit on
                pygame.draw.circle(transition_surf,(255,255,255),(self.display.get_width()//2,self.display.get_height()//2),((30 - abs(self.transition)) * 8))
                transition_surf.set_colorkey((255,255,255))
                self.display.blit(transition_surf,(0,0))

            self.display_2.blit(self.display, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake/2,random.random() * self.screenshake - self.screenshake/2)

            #bliting self.display on the self.screen
            #pygame.transform.scale(<which surface to scale>,<New Size>)
            # a.get_size() return the size of surface a
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)  # to run our code at 60 fps

Game().run()
