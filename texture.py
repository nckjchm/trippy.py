import pygame, math

class Texture:
    def __init__(self):
        pass
    
    def act(self):
        pass
    
    def draw(self, surface):
        pass
    
class ColorFill(Texture):
    def __init__(self, color):
        Texture.__init__(self)
        self.color = color
        
    def draw(self, surface, area = None):
        if area is not None:
            surface.fill(self.color, area)
        else:
            surface.fill(self.color)
        
class FluctuatingFill(ColorFill):
    stdspeedfactor = 0.15
    stdamplitude = 80
    
    def __init__(self, color, speedfactor = stdspeedfactor, amplitude = stdamplitude):
        ColorFill.__init__(self, color)
        self.basecolor = color
        self.age = 0
        self.speedfactor = speedfactor
        self.amplitude = amplitude
        
    def animate(self):
        self.animatecolor()
        self.age +=1
        
    def animatecolor(self):
        self.color = [ self.color_transform_sin_age(colorvalue) for colorvalue in self.basecolor ]
        
    def color_transform_sin_age(self, colorvalue):
        return max(0, min(255, colorvalue + self.sin_age_amplitude()))
    
    def sin_age_amplitude(self):
        return int(self.amplitude * math.sin(self.speedfactor * self.age))
        
    def act(self):
        self.animate()
