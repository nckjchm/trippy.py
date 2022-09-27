import pygame

class Background:
    def __init__(self, texture):
        self.texture = texture
        
    def draw(self, screen):
        self.texture.draw(screen)
