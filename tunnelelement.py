import pygame

"""
The Tunnel Element Class
A Tunnel Element is an individual layer of the Tunnel
Each layer is rendered independently with an inline polygon
in the color of the surfaces colorkey to make the inline 
area transparent when blitting it to the screen
A Tunnel Element individually rotates and zooms out until
it hits a scale factor where it's not on screen anymore 
and expires
"""
class TunnelElement:
    stdfadeout = 11
    
    #initialization of the TunnelElement object
    #each object starts as a colored plane with a small transparent
    #inline and the hole formed by that inline grows and rotates
    def __init__(self, inline, texture, tunnel):
        #current rotation angle of the inline polygon
        self.current_angle = 0.0
        #angle by which the inline rotates each game tick
        self.rotation_angle = 1.0
        #current scale of the inline polygon
        self.current_scale = 0.2
        #factor by which the current_scale zooms next tick
        self.zoom_factor = 0.1
        self.inline = inline
        self.texture = texture
        self.tunnel = tunnel
        #initializates the own surface as a pygame surface object of the
        #current display size
        self.surface = None
        self.resetsurface()
        
    #draw method
    #draws the Tunnel Elements individual surface
    def draw(self):
        #checks whether the surface size has changed
        #if so initializates a new surface of according size
        self.checksurface()
        #draws the texture
        self.texture.draw(self.surface)
        #draws the inline polygon
        #returns a tuple of the surface and the inline polygons bounding rect
        return self.surface, self.inline.draw(self.surface)
    
    #sets the own surface to a pygame surface object of the current screensize
    def resetsurface(self):
        if self.surface is not None:
            del self.surface
        self.surface = pygame.Surface(self.tunnel.maincontroller.screensize)
        self.surface.set_colorkey(self.tunnel.maincontroller.keycolor)
        
    #checks whether the screensize has changed and induces resetsurface accordingly
    def checksurface(self):
        if self.surface.get_rect().size != self.tunnel.maincontroller.screensize:
            self.resetsurface()
    
    #act method for handling the necessary behavior
    def act(self):
        #calls the textures act method
        #for example a fluctuatingfill will calculate its current color value here
        self.texture.act()
        #rotate, zoom and offset the inline object according to the current status
        self.inline.dotransformation(self.current_angle, self.current_scale, pygame.Vector2(self.tunnel.maincontroller.screensize) // 2)
        #set the transform values for the next tick
        self.updatetransforms()
        #check for expiration
        self.expire()
    
    #set the transform values for the next tick
    def updatetransforms(self):
        #update current rotation angle
        self.current_angle += self.rotation_angle
        #update zoom factor and scale factor
        self.current_scale += self.zoom_factor
        self.zoom_factor *= 1.01
        
    #remove method to clean self up
    def remove(self):
        self.tunnel.elements.remove(self)
        del self
        
    #expire method to check own status for expiration and call remove accordingly
    def expire(self):
        if self.current_scale > TunnelElement.stdfadeout:
            self.remove()
            
    #helper method to inverse the own elements turn direction
    def inverse_turndirection(self):
        self.rotation_angle = -self.rotation_angle
  
