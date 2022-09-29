import pygame
import pygame.gfxdraw

#The inline class handles drawing a scalable and rotatable colored 
#polygon to the screen.
#Currently it is only used to draw polygons in colorkey color, thereby
#making the area of that polygon transparent when blitting the surface
class Inline:
    keycolor = (255,0,255)
    
    def __init__(self, points, color = keycolor):
        #the points define the drawn rectangle as vectors of the corner
        #points with 0,0 as the middle of the screen
        self.points = points
        #the transformedpoints are calculated in every act step and represent
        #the rotated saled and screenspace transferred polygon
        self.transformedpoints = points[:]
        self.color = color
        
    #the draw method draws the polygon from the transformed points
    def draw(self, surface):
        return pygame.draw.polygon(surface, self.color, self.transformedpoints)
        
    #the rotate method resets the transformed points list and fills it with a
    #list of the original points rotated by the given angle
    #the transformed points describe the same polygon as the original points
    #rotated by the given angle after running this
    def rotate(self, angle):
        transformedpoints = []
        for i in range(len(self.points)):
            transformedpoints.insert(i, self.points[i].rotate(angle))
        self.transformedpoints = transformedpoints
    
    #the scale method multiplies the vector of all points in the transformed 
    #points list with the given factor
    def scale(self, factor):
        for vector in self.transformedpoints:
            vector *= factor
            
    #the dotransformation method transforms the polygon given by the points list
    #the resulting polygon is saved in the transformedpoints list
    def dotransformation(self, angle, factor, offsets):
        self.rotate(angle)
        self.scale(factor)
        for vector in self.transformedpoints:
            vector += offsets
            
#the FastInline class is a faster implementation of the Inline class
#The speed gain is achieved by using the experimental pygame.gfxdraw module
#the polygon drawing method provided by that module is faster, but doesn't
#return the bounding Rectangle of the drawn polygon, so it has to be calculated
#manually in every step
class FastInline(Inline):
    def __init__(self, points, color = Inline.keycolor):
        Inline.__init__(self, points, color)
        #the bounding rect is a pygame.rect object that represents the bounding
        #rectangle of the Inlines transformed polygon
        self.boundingrect = None
        
    #the dotransformation method of the Inline class is expanded to also calculate
    #the bounding rectangle of the transformed polygon
    def dotransformation(self, angle, factor, offsets):
        Inline.dotransformation(self, angle, factor, offsets)
        xvals = [ point.x for point in self.transformedpoints ]
        yvals = [ point.y for point in self.transformedpoints ]
        xmin = min(xvals)
        ymin = min(yvals)
        self.boundingrect = pygame.Rect(xmin, ymin, max(xvals) - xmin, max(yvals) - ymin)
        
    #the draw method is overwritten to make use of the pygame.gfxdraw.filled_polygon
    #method and returns the polygons bounding rect to match the pygame.draw.polygon
    #implementations behavior
    def draw(self, surface):
        pygame.gfxdraw.filled_polygon(surface, self.transformedpoints, self.color)
        return self.boundingrect
        
#A basic rectangle formed Inline Object that can easily be instanciated by giving
#a width (x) and height (y) value
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
        
#A basic hexagon formed Inline Object that can easily be instanciated by giving a radius (distance between middle and any corner of the hexagon) value
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
        
        
#A basic square formed Inline Object of constant size (side length = 100) to be
#easily instanciated without any additional arguments
class BaseSquare(Rectangle):
    def __init__(self):
        Rectangle.__init__(self, 100, 100)
        
#A basic Hexagon formed Inline object of constant size (radius = 100) to be easily
#instanciated without any additional arguments
class BaseHex(Hexagon):
    def __init__(self):
        Hexagon.__init__(self, 100)
