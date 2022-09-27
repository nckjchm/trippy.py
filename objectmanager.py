from multilineobject import *
import importlib, random

class ObjectManager:
    def __init__(self, maincontroller):
        self.maincontroller = maincontroller
        self.objects = []
        self.initiator = self.ObjectInitiator(self)
        
    def act(self):
        self.initiator.act()
        for obj in self.objects:
            obj.act()
    
    def draw(self, screen):
        for obj in self.objects:
            surface, screenspace = obj.draw()
            screen.blit(surface, screenspace, screenspace)
            
    class ObjectInitiator:
        zoomlineobjects = [ "ScrollLineTunnel" ]
        
        def __init__(self, manager):
            self.manager = manager
            multilineobjectmodule = importlib.import_module("multilineobject")
            self.zoomobjectclasses = [ getattr(multilineobjectmodule, obj) for obj in ObjectManager.ObjectInitiator.zoomlineobjects ]
            
        def act(self):
            if len(self.manager.objects) < 2:
                self.spawnzoomlineobject()
                
        def spawnzoomlineobject(self):
            self.addzoomlineobject(self.getzoomlineobject())
            
        def getzoomlineobject(self):
            return self.zoomobjectclasses[random.randrange(len(self.zoomobjectclasses))](self.manager)
        
        def addzoomlineobject(self, obj):
            self.manager.objects.append(obj)
            
