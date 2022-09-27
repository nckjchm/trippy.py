import pygame, time, sys
import cProfile, pstats
from pygame.locals import *
from tunnel import *
from tunnelelement import *
from inline import *
from texture import *
from background import *
from objectmanager import *

#the main function initiating the program and entering the while running status loop
def main():
    pygame.init()
    maincontroller = MainController()
    #main loop
    while maincontroller.running:
        #check whether the program is quit by the user
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                maincontroller.running = False
                maincontroller.shutdown()
        #induce tick checking
        if maincontroller.running:
            maincontroller.checktick()
    
#The main control flow unit
class MainController:
    tps = 30
    ticktime = 1000000000 // tps
    stdresolution = (600,400)
    backgroundcolor = [127,127,127]
    keycolor = (255,0,255)
    
    #The main controller initializes all other structurally important elements
    def __init__(self):
        #First command line arguments are parsed
        #Running status is set to false in case of invalid argument structure
        self.readkwargs()
        #screensize is initialized with 0 0 if not else given, a standard resolution is used in that case
        if self.screensize == (0, 0):
            self.screensize = MainController.stdresolution
        if not self.fullscreen:
            self.screen = pygame.display.set_mode(self.screensize, pygame.RESIZABLE)
        else:
            self.initfullscreen()
        #Initialization of the Background (Grey Plane)
        bgtexture = ColorFill(MainController.backgroundcolor)
        self.background = Background(bgtexture)
        #Initialization of the Tunnel Manager
        if self.notunnel:
            self.tunnel = None
        elif self.multithreading:
            self.tunnel = ImprovedMultiThreadedTunnel(self)
        else:
            self.tunnel = Tunnel(self)
        #Initialization of the Object Manager
        self.objectmanager = ObjectManager(self)
        self.objectmanager.objects = [ StaticLineTree(self.objectmanager) ]
        #initiating timing variables
        self.nexttick = time.time_ns() - MainController.ticktime
        self.framecount = 0
        self.nextprofile = self.profiletiming
        
    #command line parsing function
    def readkwargs(self):
        #initialization of all values as base case
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
        #argument parsing loop
        while i < len(args):
            #fullscreen argument
            if args[i] == "fullscreen" or args[i] == "fs":
                self.fullscreen = True
            #initial resolution argument
            #read the following 2 keywords as width and height
            elif args[i] == "sreensize" or args[i] == "ss":
                self.screensize = (int(args[i + 1]), int(args[i + 2]))
                i += 2
            #run timing argument
            elif args[i] == "t" or args[i] == "dotiming":
                self.dotiming = True
            #multithreaded tunnel rendering argument
            elif args[i] == "multithreading" or args[i] == "mt":
                self.multithreading = True
            #no tunnel rendering argument
            elif args[i] == "notunnel" or args[i] == "nt":
                self.notunnel = True
            #run profiling argument
            #read the following argument as the amount of ticks between individual profiling runs
            elif args[i] == "profiling" or args[i] == "pr":
                self.profiling = True
                if len(args) > i + 1:
                    self.profiletiming = int(args[i + 1])
                    i += 1
                else:
                    print("Argument error: Profiling argument expects additional value (time between profiling runs in ticks)")
                    self.running = False
            #base case: invalid argument, dont run program (instructions unclear)
            else:
                self.running = False
            i += 1
            
    #keyboard input induced behavior
    def keyboardinputs(self):
        keys = pygame.key.get_pressed()
        #quit program when escape press is registered
        if keys[K_ESCAPE]:
            self.running = False
        
    #helper function to capsule fullscreen initialization behavior 
    def initfullscreen(self):
        displayinfo = pygame.display.Info()
        self.screensize = (displayinfo.current_w, displayinfo.current_h)
        #vsync to minimize visual shredding
        flags = pygame.FULLSCREEN | pygame.SCALED
        self.screen = pygame.display.set_mode(self.screensize, flags, vsync = 1)

    #tick timing checker
    #is run in every iteration of the main loop
    #checks whether its time to produce the next tick
    #runs dotick method accordingly
    def checktick(self):
        if time.time_ns() > self.nexttick:
            self.nexttick += MainController.ticktime
            self.dotick()
            if time.time_ns() > self.nexttick:
                print("lagging")
                
    #calculates the amount of time that the program is behind its schedule
    def calculate_delay(self):
        return time.time_ns() - self.nexttick
    
    #the shutdown method that is invoked when the program closes
    def shutdown(self):
        print("Shutting down")
        if self.dotiming:
            print(f"Delay: {self.calculate_delay()} Nanoseconds")
    
    #the dotick function
    #invoked by checktick
    #invokes the act and draw functions or the profiled or timed versions of itself
    def dotick(self):
        #check for keyboard inputs
        self.keyboardinputs()
        if self.dotiming:
            self.dotimedtick()
        elif self.profiling and self.framecount > self.nextprofile:
            self.doprofiledtick()
        else:
            self.act()
            self.draw()
        #updates the screen after new frame is produced
        pygame.display.flip()
        self.framecount += 1
        
    #the profiled version of the dotick method
    #uses the cprofile and pstats library to run, order and output profiling data
    #dumps profiling data to a file called "frameprofil.prof" in the project dir
    def doprofiledtick(self):
        with cProfile.Profile() as pr:
            self.act()
            self.draw()
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats()
        stats.dump_stats(filename="frameprofil.prof")
        self.nextprofile += self.profiletiming
            
    #the timed version of the dotick method
    #collects timing data on the act and draw methods and outputs them
    def dotimedtick(self):
        time0 = time.time_ns()
        self.act()
        time1 = time.time_ns()
        self.draw()
        time2 = time.time_ns()
        print(f"Tick timing results: Tick time:     {time2 - time0}ns\n                     Acting time:   {time1 - time0}ns\n                     Drawing time:  {time2 - time1}ns")
        
    #the draw function building the next frame from the new state of all elements
    def draw(self):
        #background is drawn to reset the frame
        if self.background is not None:
            self.background.draw(self.screen)
        #tunnel is drawn on top of the background
        if self.tunnel is not None:
            self.tunnel.draw(self.screen)
        #visual objects are drawn on top of the rest of the frame
        if self.objectmanager is not None:
            self.objectmanager.draw(self.screen)
    
    #the act function inducing all behavior to transform the objects for the next frame
    def act (self):
        #checks whether the screen resolution has changed
        self.checksize()
        #act method for tunnel manager is induced
        if self.tunnel is not None:
            self.tunnel.act()
        #act method for visual object manager is induced
        if self.objectmanager is not None:
            self.objectmanager.act()
        
    #updates the screensize value on every frame
    def checksize(self):
        self.screensize = pygame.display.get_surface().get_rect().size
        
#run main function
if __name__=="__main__":
    main()
    
