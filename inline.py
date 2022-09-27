import pygame
import pygame.gfxdraw

class Inline:
    keycolor = (255,0,255)
    
    def __init__(self, points, color = keycolor):
        self.points = points
        self.transformedpoints = points[:]
        self.color = color
        
    def draw(self, surface):
        return pygame.draw.polygon(surface, self.color, self.transformedpoints)
        
    def rotate(self, angle):
        transformedpoints = []
        for i in range(len(self.points)):
            transformedpoints.insert(i, self.points[i].rotate(angle))
        self.transformedpoints = transformedpoints
    
    def scale(self, factor):
        for vector in self.transformedpoints:
            vector *= factor
            
    def dotransformation(self, angle, factor, offsets):
        self.rotate(angle)
        self.scale(factor)
        for vector in self.transformedpoints:
            vector += offsets
            
class FastInline(Inline):
    def __init__(self, points, color = Inline.keycolor):
        Inline.__init__(self, points, color)
        self.boundingrect = None
        
    def dotransformation(self, angle, factor, offsets):
        Inline.dotransformation(self, angle, factor, offsets)
        xvals = [ point.x for point in self.transformedpoints ]
        yvals = [ point.y for point in self.transformedpoints ]
        xmin = min(xvals)
        ymin = min(yvals)
        self.boundingrect = pygame.Rect(xmin, ymin, max(xvals) - xmin, max(yvals) - ymin)
        
    def draw(self, surface):
        pygame.gfxdraw.filled_polygon(surface, self.transformedpoints, self.color)
        return self.boundingrect
        
class Rectangle(FastInline):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        x2 = x//2
        y2 = y//2
        Inline.__init__(self, [pygame.Vector2(-x2, -y2),
                       pygame.Vector2(+x2, -y2),
                       pygame.Vector2(+x2, +y2),
                       pygame.Vector2(-x2, +y2)])
        
class Hexagon(FastInline):
    apothem = 0.866
    
    def __init__(self, radius):
        self.radius = radius
        relative_apothem = Hexagon.apothem * radius
        relative_apothem2 = relative_apothem / 2
        Inline.__init__(self, [pygame.Vector2(-radius, 0),
                       pygame.Vector2(-relative_apothem2, -relative_apothem),
                       pygame.Vector2(relative_apothem2, -relative_apothem),
                       pygame.Vector2(radius, 0),
                       pygame.Vector2(relative_apothem2, relative_apothem),
                       pygame.Vector2(-relative_apothem2, relative_apothem)])
        
        
class BaseSquare(Rectangle):
    def __init__(self):
        Rectangle.__init__(self, 100, 100)
        
class BaseHex(Hexagon):
    def __init__(self):
        Hexagon.__init__(self, 100)
