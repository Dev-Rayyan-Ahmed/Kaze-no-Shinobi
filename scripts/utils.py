import pygame
import os

BASE_IMG_PATH = "data/images/"

def load_image(path):
    # .convert() changes internal representation of img and allows efficient rendering
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0)) #for Transparent BG Black color of all iamges
    return img

def load_images(path):
    images = []
    for img_name in os.listdir(BASE_IMG_PATH+path):
        images.append(load_image(path+"/"+img_name))
    return images

# Animations
# images = list of images we want to animate
# img_dur = how many frames animation takes/show for
# loop, set to True; by default we want our animations to loop
class Animation:
    def __init__(self, images, img_dur=5,loop=True):
        self.images = images
        self.img_duration = img_dur
        self.loop = loop
        self.done = False #specify that we are done with animation/looping
        self.frame = 0 #fram of the game

    #list1 = list2
    # doesn't copy list, but it's like a reference to it
    #changing list2 will affect the list1
    # so, to our benefit we can copy as much as we want, and all the images would be a
    # reference to the same list, no extra memory taking

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame+1) % (self.img_duration * len(self.images))
            #                             < equal to total no. of frames for the animation>
            #if frame == total_frames then % == 0 ; resets the animation
            #if len = 3 and duration = 5 ; then total frames = 15 (that's how long is out animation)
            # that doesn't mean we need 15 images in the list
        else:
            self.frame = min((self.frame+1),self.img_duration*len(self.images) -1)
            # -1 because in list index starts from 0 and here we always get +1 answers
            if self.frame >= self.img_duration * len(self.images):
                self.done = True # to specify animation has ended

    def img(self):

        return self.images[int(self.frame / self.img_duration)]
        # since int() it will be 0 , 1 , 2 -- -- -  --
        # because of that we know the answer would be 1 2 3 only when frame == img_duration (reaching threshold)
        # or double or triple and that's the index we are using to change our index





