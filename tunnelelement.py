import pygame

class TunnelElement:
    stdfadeout = 11
    
    def __init__(self, inline, texture, tunnel):
        self.current_angle = 0.0
        self.rotation_angle = 1.0
        self.current_scale = 0.2
        self.zoom_factor = 0.1
        self.alpha = 255
        self.inline = inline
        self.texture = texture
        self.tunnel = tunnel
        self.surface = None
        self.resetsurface()
        
    def draw(self):
        self.checksurface()
        self.texture.draw(self.surface)
        return self.surface, self.inline.draw(self.surface)
    
    def resetsurface(self):
        if self.surface is not None:
            del self.surface
        self.surface = pygame.Surface(self.tunnel.maincontroller.screensize)
        self.surface.set_colorkey(self.tunnel.maincontroller.keycolor)
        
    def checksurface(self):
        if self.surface.get_rect().size != self.tunnel.maincontroller.screensize:
            self.resetsurface()
    
    def act(self):
        self.texture.act()
        self.inline.dotransformation(self.current_angle, self.current_scale, pygame.Vector2(self.tunnel.maincontroller.screensize) // 2)
        self.updatetransforms()
        self.expire()
    
    def updatetransforms(self):
        self.current_angle += self.rotation_angle
        self.current_scale += self.zoom_factor
        self.zoom_factor *= 1.01
        
    def remove(self):
        self.tunnel.elements.remove(self)
        del self
        
    def expire(self):
        if self.current_scale > TunnelElement.stdfadeout:
            self.remove()
            
    def inverse_turndirection(self):
        self.rotation_angle = -self.rotation_angle
  
