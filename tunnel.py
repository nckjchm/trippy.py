import pygame, random, importlib
import concurrent.futures
import asyncio
from texture import *
from tunnelelement import *
from inline import *

class Tunnel:
    maxelements = 8
    
    def __init__(self, maincontroller):
        self.maxelements = Tunnel.maxelements
        self.elements = []
        self.maincontroller = maincontroller
        self.initiator = ElementInitiator(self)
        
    def act(self):
        self.initiator.act()
        for element in self.elements:
            element.act()
                
    def draw(self, screen):
        surfacedata = [ element.draw() for element in self.elements ]
        maxindex = len(surfacedata) - 1
        index = 0
        while index < maxindex:
            screen.blit(surfacedata[index][0], surfacedata[index + 1][1], surfacedata[index + 1][1])
            index += 1
        if maxindex >= 0:
            screen.blit(surfacedata[index][0], (0,0))
            
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
                
    
class ImprovedMultiThreadedTunnel(MultiThreadedTunnel):
    def drawandact(self, element, screen):
        element.act()
        return element.draw()
    
    def act(self):
        self.initiator.act()
    
    def draw(self, screen):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [None for _ in range(len(self.elements))]
            for index, element in enumerate(self.elements):
                futures[index] = executor.submit(self.drawandact, element, screen)
            results = []
            for index, future in enumerate(futures):
                results.append(future.result())
                if index > 0:
                    screen.blit(results[index - 1][0], results[index][1], results[index][1])
            if len(results) > 0:
                screen.blit(results[-1][0], (0,0))
                

class ElementInitiator:
    inlines = [ "BaseHex" ]
    basefrequency = 7
    
    def __init__(self, tunnel, frequency = basefrequency):
        self.tunnel = tunnel
        inlinemodule = importlib.import_module("inline")
        self.inlines = [ getattr(inlinemodule, inline) for inline in ElementInitiator.inlines ]
        self.wildness = 1
        self.colors = [[228,12,24], [12,228,24], [12,24,228]]
        self.lastcolor = 0
        self.frequency = frequency
        self.clock = frequency + 1
        
    def getelement(self):
        return TunnelElement(self.inlines[random.randrange(len(self.inlines))](), self.nextcolor(), self.tunnel)
    
    def addelement(self, element):
        self.tunnel.elements.insert(0, element)
        
    def nextcolor(self):
        index = random.randrange(len(self.colors) - 1)
        if index == self.lastcolor:
            index += 1
        self.lastcolor = index
        return FluctuatingFill(self.colors[index])
        
    def randomize_element(self, element):
        if bool(random.getrandbits(1)):
            element.inverse_turndirection()
        
    def act(self):
        self.clock += 1
        if self.clock > self.frequency:
            self.clock = 0
            element = self.getelement()
            self.randomize_element(element)
            self.addelement(element)
            
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
