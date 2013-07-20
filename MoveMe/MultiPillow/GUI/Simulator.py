#import pygame and the system library
import sys, pygame, random
from pygame.locals import *
from GraphicPillow import *
from MoveMe.MultiPillow.Room import *

class Simulator:
    def __init__(self, delayTime = 10, resolution=(1024,640), bgColor=(255,255,255)):
        pygame.init()
        ''' Private properties '''
        self.__pillowId  = 0
        
        ''' Configure settings '''
        self.bgColor     = bgColor
        self.delayTime = delayTime
        self.resolution  = resolution
        ''' Initalise screen '''
        self.initScreen()
        
        ''' Add event, mouse and group '''
        self.event = pygame.event.poll() 
        self.mouse = Mouse()
        self.group = pygame.sprite.RenderUpdates()        
        
        ''' Create Room '''
        self.room  = Room()        

    def getNewId(self):
        self.__pillowId += 1
        return self.__pillowId

    def initScreen(self):
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption('MoveMe simulator.')
        self.background = pygame.Surface(self.resolution)
        self.background.fill(self.bgColor)
        self.screen.blit(self.background, (0, 0))
        #pygame.time.delay(100)
        pygame.display.update()

    def addSprites(self):
        self.insertPillow()
                  
    def addSprites2(self):
        self.insertPillow()
        
        ''' Add Sprite Machine'''
        SpriteMachine(self.group, (250,300),(700,400))
        
        ''' Add Rectangles '''
        for (color, location) in [([255, 0, 0], [300, 0])
                                 ,([0, 255, 0], [300, 300])
                                 ,([0, 255, 0], [800, 300])
                                 ,([0, 0, 255], [300, 100])
                                 ]:
            self.group.add(Rect(color, (0,0),location))
            
        ''' Add circles '''
        self.group.add(MotionCircle((255,0,0), 20, 0, (750,0), (800,500)))
        self.group.add(MotionCircle((0,0,255), 20, 0, [0, 255], [0, 300]))
        self.group.add(MotionCircle((255,255,0), 20, 0, (750,0), (0,400)))
        self.group.add(MotionCircle((255,0,0), 20, 0, (750,0), (100,400)))
        self.group.add(MotionCircle((255,0,0), 20, 0, (400,250), (400,250)))
        
    def insertPillow(self, name):
        gpillow = GraphicPillow(self.getNewId(), self.group, self.randPosition())
        gpillow.statePillow.name = name
        self.room.addPillow(gpillow.statePillow)
       
        return gpillow.getId()
        
    def removePillow(self, pillowId):
        ''' remove pillow from sprite group '''
        for gpillow in self.group:
            if gpillow.__class__.__name__ == 'GraphicPillow' and gpillow.getId() == pillowId: gpillow.remove()
        ''' remove pillow from room '''

    def randPosition(self):
        ''' Get a random position far from the borders '''
        xloc = self.resolution[0] - 100
        yloc = self.resolution[1] - 100

        pos = [ random.randrange(100, xloc)
              , random.randrange(100, yloc)]
        
        return pos

    def updateDisplay(self, mouse):
        # Clean self.screen
        self.group.clear(self.screen, self.background)
        # Call sprites update function 
        self.group.update(pygame.time.get_ticks(), mouse)
        # Draw result to self.screen surface 
        rectlist = self.group.draw(self.screen)
        # Update portions of the screen
        pygame.display.update(rectlist)
    
    def handleInput(self):
        ''' enable window quit button '''
        if self.event.type == pygame.QUIT: 
            sys.exit()        
        
        ''' Mouse '''
        self.mouse.update(pygame.time.get_ticks(), self.event)
        
        ''' Keyboard '''
        self.key = ''
        if self.event.type == KEYDOWN:
            #print self.event.unicode
            self.key = self.event.unicode
                       
            ''' pressing f toggles fullscreen '''
            if self.key == 'f': 
                pygame.display.toggle_fullscreen()
                print 'fullscreen'                       
            ''' pressing q quits '''
            if self.key == 'q': 
                print 'Quit.'
                sys.exit()
            if self.key == 'r':
                self.removePillow(1)
            if self.key == 'a':
                self.insertPillow()
            ''' pressing g shows group formation '''
            if self.key == 'g':
                result = []
                for group in self.room.groups:
                    print group.pillows
                    print 'group (',group.id,')'
                    for pillowId in group.pillows:
                        pillow = group.pillows[pillowId]
                        if pillow.sourcePillow: p = pillow.sourcePillow.move.position
                        else: 
                            p = 1
                        result.append((pillow.id,pillow.getSourceId(), p))
                print result
                
    def update2(self):
            ''' 0. Update room '''
            self.room.run()
            ''' 1. handle input '''
            self.handleInput()
            ''' 2. update sprites and display '''
            self.updateDisplay(self.mouse)
            ''' 3. wait '''
            #pygame.time.wait(self.delayTime)
            ''' 4. Fetch new event.'''
            self.event = pygame.event.poll()


    def update(self):
            ''' 1. Fetch new event.'''
            self.event = pygame.event.poll()
            ''' 2. Update room '''
            self.room.run()
            ''' 3. handle input '''
            self.handleInput()
            ''' 4. update sprites and display '''
            self.updateDisplay(self.mouse)
            ''' 5. wait '''
            #pygame.time.wait(self.delayTime)

    def run(self):
        self.addSprites()
        while 1:
            self.update()
            ''' 5. wait '''
            pygame.time.wait(self.delayTime)

'''
    Mouse Controler: add functionality: drag,...
'''
class Mouse:
    def __init__(self):
        self.nextUpdateTime = 0 # update() hasn't been called yet.        
        self.position       = pygame.mouse.get_pos()
        
        ''' mouse properties '''
        self.drag           = False
        self.buttons        = (0,0,0) 
        
    def update(self, currentTime, event):
        ''' Update every 10 milliseconds = 1/100th of a second. '''
        if self.nextUpdateTime < currentTime:          
            self.nextUpdateTime = currentTime + 10   
            self.position       = pygame.mouse.get_pos()

            ''' Drag and Drop '''
            if event.type == MOUSEBUTTONUP:
                self.drag = False          
            elif event.type == MOUSEBUTTONDOWN:
                self.buttons = pygame.mouse.get_pressed()           
                self.drag = True
            else:
                self.buttons = (0,0,0)

''' ------------------------------------------------------------------------ '''
''' Main definition                                                          '''
''' ------------------------------------------------------------------------ '''
def main():
    simulator = Simulator()
    simulator.run()

if __name__ == '__main__': main()
