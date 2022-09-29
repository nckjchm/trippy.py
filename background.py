import pygame

#The background class
#Handles drawing a texture to the entire screen in order to
#reset it at the start of the drawing step of a tick
class Background:
    #the background is initialized with a texture object
    def __init__(self, texture):
        self.texture = texture
        
    #the draw method draws the background texture to the entire screen
    def draw(self, screen):
        self.texture.draw(screen)
