import pygame, time, sys
import cProfile, pstats
from tunnel import *
from tunnelelement import *
from inline import *
from texture import *
from background import *
from objectmanager import *

def main():
    pygame.init()
    maincontroller = MainController()
    while maincontroller.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                maincontroller.running = False
                maincontroller.shutdown()
        if maincontroller.running:
            maincontroller.checktick()
    
    
class MainController:
    tps = 30
    ticktime = 1000000000 // tps
    stdresolution = (600,400)
    backgroundcolor = [127,127,127]
    keycolor = (255,0,255)
    
    def __init__(self):
        self.readkwargs()
        if self.screensize == (0, 0):
            self.screensize = MainController.stdresolution
        if not self.fullscreen:
            self.screen = pygame.display.set_mode(self.screensize, pygame.RESIZABLE)
        else:
            self.initfullscreen()
        bgtexture = ColorFill(MainController.backgroundcolor)
        self.background = Background(bgtexture)
        if self.notunnel:
            self.tunnel = None
        elif self.multithreading:
            self.tunnel = ImprovedMultiThreadedTunnel(self)
        else:
            self.tunnel = Tunnel(self)
        self.objectmanager = ObjectManager(self)
        self.objectmanager.objects = [ StaticLineTree(self.objectmanager) ]
        self.nexttick = time.time_ns() - MainController.ticktime
        self.framecount = 0
        self.nextprofile = self.profiletiming
        
    def readkwargs(self):
        self.running = True
        self.fullscreen = False
        self.screensize = (0,0)
        self.dotiming = False
        self.multithreading = False
        self.notunnel = False
        self.profiling = False
        self.profiletiming = 0
        args = sys.argv
        i = 1
        while i < len(args):
            if args[i] == "fullscreen" or args[i] == "fs":
                self.fullscreen = True
            elif args[i] == "sreensize" or args[i] == "ss":
                self.screensize = (int(args[i + 1]), int(args[i + 2]))
                i += 2
            elif args[i] == "t" or args[i] == "dotiming":
                self.dotiming = True
            elif args[i] == "multithreading" or args[i] == "mt":
                self.multithreading = True
            elif args[i] == "notunnel" or args[i] == "nt":
                self.notunnel = True
            elif args[i] == "profiling" or args[i] == "pr":
                self.profiling = True
                if len(args) > i + 1:
                    self.profiletiming = (int(args[i + 1]))
                    i += 1
                else:
                    print("Argument error: Profiling argument expects additional value (time between profiling runs in ticks)")
                    self.running = False
            else:
                self.running = False
            i += 1
        
    def initfullscreen(self):
        displayinfo = pygame.display.Info()
        self.screensize = (displayinfo.current_w, displayinfo.current_h)
        flags = pygame.FULLSCREEN | pygame.SCALED
        self.screen = pygame.display.set_mode(self.screensize, flags, vsync = 1)

        
    def checktick(self):
        if time.time_ns() > self.nexttick:
            self.nexttick += MainController.ticktime
            self.dotick()
            if time.time_ns() > self.nexttick:
                print("lagging")
                
    def calculate_delay(self):
        return time.time_ns() - self.nexttick
    
    def shutdown(self):
        print("Shutting down")
        if self.dotiming:
            print(f"Delay: {self.calculate_delay()} Nanoseconds")
    
    def dotick(self):
        if self.dotiming:
            self.dotimedtick()
        elif self.profiling and self.framecount > self.nextprofile:
            self.doprofiledtick()
        else:
            self.act()
            self.draw()
        pygame.display.flip()
        self.framecount += 1
        
    def doprofiledtick(self):
        with cProfile.Profile() as pr:
            self.act()
            self.draw()
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats()
        stats.dump_stats(filename="frameprofil.prof")
        self.nextprofile += self.profiletiming
            
    def dotimedtick(self):
        time0 = time.time_ns()
        self.act()
        time1 = time.time_ns()
        self.draw()
        time2 = time.time_ns()
        print(f"Tick timing results: Tick time:     {time2 - time0}ns\n                     Acting time:   {time1 - time0}ns\n                     Drawing time:  {time2 - time1}ns")
        
    def draw(self):
        if self.background is not None:
            self.background.draw(self.screen)
        if self.tunnel is not None:
            self.tunnel.draw(self.screen)
        if self.objectmanager is not None:
            self.objectmanager.draw(self.screen)
        
    def act (self):
        self.checksize()
        if self.tunnel is not None:
            self.tunnel.act()
        if self.objectmanager is not None:
            self.objectmanager.act()
        
    def checksize(self):
        self.screensize = pygame.display.get_surface().get_rect().size
        

if __name__=="__main__":
    main()
    
