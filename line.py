import pygame

class Line:
    stdwidth = 1
    stdcolor = [255,255,255]
    
    def __init__(self, startpoint, endpoint, color = stdcolor, width = stdwidth):
        self.startpoint = startpoint
        self.endpoint = endpoint
        self.transformedstartpoint = None
        self.transformedendpoint = None
        self.width = width
        self.color = color
        
    def rotate(self, angle):
        self.transformedstartpoint = self.transformedstartpoint.rotate(angle)
        self.transformedendpoint = self.transformedendpoint.rotate(angle)
        
    def scale(self, factor):
        self.transformedstartpoint *= factor
        self.transformedendpoint *= factor
            
    def dotransformation(self, angle, factor, offsets):
        self.transformedstartpoint = pygame.Vector2(self.startpoint)
        self.transformedendpoint = pygame.Vector2(self.endpoint)
        self.rotate(angle)
        self.scale(factor)
        self.transformedstartpoint += offsets
        self.transformedendpoint += offsets
        
    def draw(self, surface):
        return pygame.draw.line(surface, self.color, self.transformedstartpoint, self.transformedendpoint, self.width)
