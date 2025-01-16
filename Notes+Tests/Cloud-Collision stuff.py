import pygame
import sys
# from scripts.entities import PhysicsEntity

class Game:
    def __init__(self):

        pygame.init()

        pygame.display.set_caption('Kaze no Shinobi')
        self.screen = pygame.display.set_mode((640, 480))

        self.clock = pygame.time.Clock()  # to run game on 60 fps

        self.img = pygame.image.load('data/images/clouds/cloud_1.png')
        self.img.set_colorkey((0, 0, 0))  # will treat that color in that image as transparency
        self.img_pos = [160, 260]
        self.movement = [False, False]

        self.collision_area = pygame.Rect(50, 50, 300, 50) # Specify a Rectangle

    def run(self):
        while True:
            self.screen.fill((14, 219, 248))

            # Creating a Rectangle for our img; which is updated at every iteration
            img_r = pygame.Rect(self.img_pos[0], self.img_pos[1], self.img.get_width(), self.img.get_height())

            if img_r.colliderect(self.collision_area):
                pygame.draw.rect(self.screen, (0, 100,255 ), self.collision_area)
            #Function:          #where to draw ,  Color ,  Which Rect to Draw
            else:
                pygame.draw.rect(self.screen, (0, 50,155 ), self.collision_area)

            self.screen.blit(self.img, self.img_pos)
            self.img_pos[1] += (self.movement[0] - self.movement[1]) * 5

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.movement[0] = True
                    if event.key == pygame.K_UP:
                        self.movement[1] = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.movement[0] = False
                    if event.key == pygame.K_UP:
                        self.movement[1] = False

            pygame.display.update()
            self.clock.tick(60)  # to run our code at 60 fps


Game().run()
