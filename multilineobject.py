import pygame, math
from line import *

class MultiLineObject:
    stdexpirescale = 10
    
    def __init__(self, manager):
        self.lines = []
        self.current_angle = 0.0
        self.rotation_angle = 1.0
        self.current_scale = 0.2
        self.zoom_factor = 0.1
        self.alpha = 255
        self.manager = manager
        self.turning = False
        self.zooming = False
        self.expirescale = MultiLineObject.stdexpirescale
        
    def act(self):
        self.updatetransforms()
        self.expire()
        for line in self.lines:
            line.dotransformation(self.current_angle, self.current_scale, pygame.Vector2(self.manager.maincontroller.screensize) // 2)
            
    def updatetransforms(self):
        if self.turning:
            self.current_angle += self.rotation_angle
        if self.zooming:
            self.current_scale += self.zoom_factor
            self.zoom_factor *= 1.04
            
    def draw(self):
        surface = pygame.Surface(self.manager.maincontroller.screensize)
        surface.set_colorkey(self.manager.maincontroller.keycolor)
        surface.fill(self.manager.maincontroller.keycolor)
        rects = []
        for line in self.lines:
            rects.append(line.draw(surface))
        if len(rects) > 0:
            screenspace = rects[0]
            rects.pop(0)
        if len(rects) > 1:
            screenspace = screenspace.unionall(rects)
        else:
            screenspace = pygame.Rect(0, 0, 0, 0)
        return surface, screenspace
    
    def expire(self):
        if self.current_scale > self.expirescale:
            self.remove()
            
    def remove(self):
        self.manager.objects.remove(self)
        del self
    
class LineTree(MultiLineObject):
    stdtrunksize = 220.0
    stdbranchamount = 2
    stdbranchangle = 60
    stdbranchfactor = 0.9
    stdcolor = [255,255,255]
    stdlinewidth = 2
    
    def __init__(self, manager, trunksize = stdtrunksize, branchamount = stdbranchamount, branchangle = stdbranchangle, branchfactor = stdbranchfactor, color = stdcolor, linewidth = stdlinewidth):
        MultiLineObject.__init__(self, manager)
        self.trunksize = trunksize
        self.branchamount = branchamount
        self.branchangle = branchangle
        self.branchfactor = branchfactor
        self.color = color
        self.linewidth = linewidth
        self.trunk = self.LineTreeBranch(Line(pygame.Vector2(0, self.trunksize), pygame.Vector2(0, 0), self.color, self.linewidth), 0, self.trunksize)
        self.branches = [self.trunk]
        self.lastgeneration = [self.trunk]
        self.lines = [self.trunk.line]
        self.age = 0
        self.swayamplitude = 2
        self.breathamplitude = 8
        self.swayspeedfactor = 0.075
        self.breathspeedfactor = 0.05
    
    def getgeneration(self, amount = None, angle = None, factor = None):
        newgeneration = []
        if amount is None:
            amount = self.branchamount
        if angle is None:
            angle = self.branchangle
        if factor is None:
            factor = self.branchfactor
        for branch in self.lastgeneration:
            newgeneration.extend(branch.getchildren(amount, angle, factor))
        self.branches.extend(newgeneration)
        self.lastgeneration = newgeneration
        self.lines.extend(map(lambda branch: branch.line, newgeneration))
        
    def act(self):
        self.animate()
        MultiLineObject.act(self)
        self.age += 1
        
    def animate(self):
        swayangle = self.swayamplitude * math.sin(self.swayspeedfactor * self.age)
        breathangle = self.breathamplitude * ((math.sin(self.breathspeedfactor * self.age) / 2) + 1)
        self.animatetree(swayangle, breathangle)
        
    def animatetree(self, swayangle, breathangle):
        self.trunk.sway(swayangle)
        self.trunk.breathe(breathangle)
        self.trunk.reallign()
        
    class LineTreeBranch:
        stdswayfactor = 1.3
        
        def __init__(self, line, angle, length, parent = None):
            self.line = line
            self.baseangle = angle
            self.length = length
            self.parent = parent
            self.swayangle = 0
            self.breathangle = 0
            self.relative_angle = 0
            if self.parent is not None:
                self.relative_angle = self.baseangle - self.parent.baseangle
            self.children = None
            
        def getchildren(self, amount, relative_angle, factor):
            if self.children is not None:
                return self.children
            relativelength = self.length * factor
            rawendpoint = pygame.Vector2(0, -relativelength)
            negamountdec2 = -(amount - 1) / 2
            self.children = [ self.getchild(rawendpoint, ((negamountdec2 + i) * relative_angle) + self.baseangle, relativelength) for i in range(amount) ]
            return self.children
        
        def reallign(self):
            if self.children is not None:
                for child in self.children:
                    child.line.startpoint = self.line.endpoint
                    rawendpoint = pygame.Vector2(0, -child.length)
                    child.angle = child.baseangle + child.swayangle + child.breathangle
                    child.line.endpoint = rawendpoint.rotate(child.angle) + self.line.endpoint
                    child.reallign()
                    
        def breathe(self, angle):
            if self.children is not None:
                childcount = len(self.children)
                childcountdec2 = (childcount - 1)/2
                for index, child in enumerate(self.children):
                    factor = ( index - childcountdec2 )/childcountdec2
                    child.breathangle = angle * factor
                    child.breathe(angle)
            
        def sway(self, angle, factor = stdswayfactor):
            self.swayangle = angle
            if self.children is not None:
                nextangle = angle * factor
                for child in self.children:
                    child.sway(nextangle, factor)
            
        def getchild(self, rawendpoint, angle, length):
            transformedendpoint = rawendpoint.rotate(angle)
            transformedendpoint += self.line.endpoint
            return LineTree.LineTreeBranch(Line(self.line.endpoint, transformedendpoint, self.line.color, self.line.width), angle, length, self)
            
class StaticLineTree(LineTree):
    stddepth = 4
    
    def __init__(self, manager, depth = stddepth):
        LineTree.__init__(self, manager, branchangle = 36, branchfactor = 0.85)
        for i in range(depth):
            self.getgeneration(amount = i // 2 + 2)
    
class ScrollLines(MultiLineObject):
    
    def __init__(self, manager):
        MultiLineObject.__init__(self, manager)
        self.zooming = True
        
class ScrollLineTunnel(ScrollLines):
    
    def __init__(self, manager):
        ScrollLines.__init__(self, manager)
        self.resetlinepoints()
        
    def resetlinepoints(self):
        screensize = self.manager.maincontroller.screensize
        aspectratio = screensize[0] / screensize [1]
        initsize = 10
        lengthfactor = 0.6
        xmax = initsize * aspectratio
        ymax = initsize / aspectratio
        xmin = lengthfactor * xmax
        ymin = lengthfactor * ymax
        self.expirescale = screensize[0] / xmin
        self.lines = [ Line(pygame.Vector2(-xmin, -ymin),                  pygame.Vector2(-xmax, -ymax)), 
                      Line(pygame.Vector2(-xmin, ymin),                  pygame.Vector2(-xmax, ymax)), 
                      Line(pygame.Vector2(xmin, ymin),                  pygame.Vector2(xmax, ymax)), 
                      Line(pygame.Vector2(xmin, -ymin),                  pygame.Vector2(xmax, -ymax)) ]
        

