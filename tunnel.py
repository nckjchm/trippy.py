import pygame, random, importlib
import concurrent.futures
import asyncio
from texture import *
from tunnelelement import *
from inline import *

"""
The tunnel managing class controlling the behavior of the tunnel elements
Capsuled within is the Tunnel Element initiator class handling the initialization of
new Tunnel Elements and thereby guiding the appearance of the tunnel
"""
class Tunnel:
    maxelements = 8
    
    #initialization of the tunnel manager
    def __init__(self, maincontroller):
        self.maxelements = Tunnel.maxelements
        #the elements are initialized as an empty array that is populated with Elements at a later time
        self.elements = []
        #upward reference to the maincontroller
        self.maincontroller = maincontroller
        #initialization of the ElementInitiator
        self.initiator = ElementInitiator(self)
        
    #act method inducing the initiators and elements behavior
    def act(self):
        self.initiator.act()
        for element in self.elements:
            element.act()
                
    """
    draw method
    calls draw method on all elements
    then blits their individual surfaces to the screen in the according order
    screenspace is taken into account while blitting
    each element is only drawn within the bounds of the next higher elements inline
    the rest is not supposed to be visible anyways and blitting it takes 
    a considerable amount of time
    """
    def draw(self, screen):
        #array of each elements surface and the rect bounding their inline
        surfacedata = [ element.draw() for element in self.elements ]
        maxindex = len(surfacedata) - 1
        index = 0
        #loop blitting each element within the bound of the inline of the next
        while index < maxindex:
            screen.blit(surfacedata[index][0], surfacedata[index + 1][1], surfacedata[index + 1][1])
            index += 1
        #blitting the last element to the whole screen if there is at least one element
        if maxindex >= 0:
            screen.blit(surfacedata[index][0], (0,0))
            
"""
Multi Threaded Implementation attempt of the Tunnel Class
Child class of the tunnel class, only implements threaded versions of act and draw
No longer in use as the improved implementation is as the name suggests better
Only for redundancy
"""
class MultiThreadedTunnel(Tunnel):
    def act(self):
        self.initiator.act()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [None for _ in range(len(self.elements))]
            for index, element in enumerate(self.elements):
                futures[index] = executor.submit(element.act)
            concurrent.futures.wait(futures)
    
    def draw(self, screen):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [None for _ in range(len(self.elements))]
            for index, element in enumerate(self.elements):
                futures[index] = executor.submit(element.draw)
            for future in futures:
                screen.blit(future.result(), (0, 0))
                
"""
A more promising attempt at a MultiThreaded Implementation
Combines the draw and act method for the TunnelElements in one parallelizable function
To reduce the overhead caused by thread invocation
Problems:
The overhead is still greater than the cost
Ideas:
Maybe it's possible to implement the threads in form of an executor pool object
outside of a with block then they could be initialized at the start and only 
filled with work to execute at runtime, which would eliminate the dragging overhead
Maybe the with block has to be in the global main function and the thread pool
executor has to be passed down as a reference to this object then it could
probably also behave in the same way
"""
class ImprovedMultiThreadedTunnel(MultiThreadedTunnel):
    #parallelizable function which runs both an elements act and draw method
    #returns the return value of the element.draw call
    def drawandact(self, element, screen):
        element.act()
        return element.draw()
    
    #act metod only inducing the initiators act method because element act is
    #induced in the draw method
    def act(self):
        self.initiator.act()
    
    #MultiThreaded draw method
    #A thread is initialized for each Element and is filled with the drawandact
    #method for each element reference
    #then results are collected in order and 
    def draw(self, screen):
        #initialization of the thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            #populates a list with futuire objects each containing the return value
            #of a threads function call at a later point
            futures = [None for _ in range(len(self.elements))]
            for index, element in enumerate(self.elements):
                #call the drawandact function for each element
                futures[index] = executor.submit(self.drawandact, element, screen)
            results = []
            #await results and draw the surfaces
            #for description of how screenspace blitting is implemented see the
            #documentation of the draw method in the base Tunnel class
            for index, future in enumerate(futures):
                results.append(future.result())
                if index > 0:
                    screen.blit(results[index - 1][0], results[index][1], results[index][1])
            if len(results) > 0:
                screen.blit(results[-1][0], (0,0))
                
"""
Element initiator class
initializes the Tunnel Elements
currently initializes red/blue/green colored hexagonal shapes
Ideas:
Different modes between which the initializer switches
The hope is that interesting behavioral patterns emerge
"""
class ElementInitiator:
    inlines = [ "BaseHex" ]
    basefrequency = 7
    
    #initialization of the ElementInitiator
    #handles importing of the modules and classes needed automatically
    #pump out tunnel element objects
    def __init__(self, tunnel, frequency = basefrequency):
        #upward reference to the tunnel manager
        self.tunnel = tunnel
        inlinemodule = importlib.import_module("inline")
        #the inlines list is populated with references to the class objects
        #of the inline classes named in the inlines list
        self.inlines = [ getattr(inlinemodule, inline) for inline in ElementInitiator.inlines ]
        #not used yet, but this is where the magic is planned
        self.wildness = 1
        #three basic RGB color values: a red, green and a blue
        self.colors = [[228,12,24], [12,228,24], [12,24,228]]
        self.lastcolor = 0
        #the frequency in ticks when new elements are produced
        self.frequency = frequency
        self.clock = frequency + 1
        
    #initializes a single TunnelElement
    def getelement(self):
        return TunnelElement(self.inlines[random.randrange(len(self.inlines))](), self.nextcolor(), self.tunnel)
    
    #adds a TunnelElement to the Tunnel managers element list
    def addelement(self, element):
        self.tunnel.elements.insert(0, element)
        
    #specifies one of the three base colors as next color
    #currently returns a FluctuatingFill object with that color
    #will return different kinds of Texture objects in the future
    #doesnt pick the same color twice in a row
    def nextcolor(self):
        index = random.randrange(len(self.colors) - 1)
        if index == self.lastcolor:
            index += 1
        self.lastcolor = index
        return FluctuatingFill(self.colors[index])
        
    #randomizes the initialized element
    #currently only randomizes rotation direction
    #this is where the magic with the wildness value is planned to play out
    def randomize_element(self, element):
        if bool(random.getrandbits(1)):
            element.inverse_turndirection()
    
    #act method, increases clock and spawns element if timing is met
    def act(self):
        self.clock += 1
        if self.clock > self.frequency:
            self.clock = 0
            element = self.getelement()
            self.randomize_element(element)
            self.addelement(element)
            
#alternative deprecated implementation of the tunnel class
#kept for redundancy
class CheapTunnel(Tunnel):
    def __init__(self, maincontroller):
        Tunnel.__init__(self, maincontroller)
        colors = [FluctuatingFill([228,12,24]), FluctuatingFill([12,228,24]), FluctuatingFill([12,24,228])]
        self.elements = [TunnelElement(Rectangle(100, 100), colors[i % 3], self) for i in range(9)]
        for i in range(len(self.elements)):
            self.elements[i].current_scale += i
            
    def act(self):
        for element in self.elements:
            element.act()
            if element.current_scale > 10:
                self.elements.remove(element)
                self.elements.insert(0, TunnelElement(Rectangle(100,100), element.texture, self))
                self.randomize_movement(self.elements[0])
                del element
                
    def randomize_movement(self, element):
        if bool(random.getrandbits(1)):
            element.rotation_angle = -element.rotation_angle
