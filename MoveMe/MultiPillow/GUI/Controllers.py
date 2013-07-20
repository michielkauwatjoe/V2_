import pygame
from Shape import *

'''
    Garbage Controler: A pillow is removed when it is dragged to the garbage bin.
'''
class Garbage(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.surface = pygame.image.load('./data/garbage.jpg')
        
'''
    Line, to show dependencies between pillows
'''            
class Line(pygame.sprite.Sprite,LineShape):
    def __init__(self, id, screen=0, pos=(0,0), dest=(400,400), color=(250,0,0)):
        # Extend Sprite 
        pygame.sprite.Sprite.__init__(self)
        self.next_update_time = 0 # update() hasn't been called yet.     
        # Extend Circle Shape
        LineShape.__init__(self, (0,0,250),pos, dest)
        
        self.rect   = self.image.get_rect()
        self.show   = False
        self.id     = id
        self.source = False
        self.screen = screen


        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill([0, 0, 0]) 

        self.gunMachine = GunMachine(self.screen, self.background,(0,0),(0,0),(0,0,0),0)



    def update(self, current_time, (mouse, key), pillows):
        if key == 'g':
            self.show = not self.show
            
        if self.next_update_time < current_time:
            self.next_update_time = current_time + 10            
            
            # code goes here
            gpillow = pillows[self.id-1]
            if gpillow.pillow.getSourceId() and self.show:
                sourcePillow = pillows[gpillow.pillow.getSourceId()-1]
                #print 'line%s: ',self.id,gpillow.rect.center, sourcePillow.rect.center
                self.draw( (0,0,250), gpillow.rect.center, sourcePillow.rect.center)
                # GunMachine code
                self.gunMachine.addShots( sourcePillow.rect.center
                                        , gpillow.rect.center
                                        , sourcePillow.color
                                        )
                self.gunMachine.update(pygame.time.get_ticks(), 0)
            else:
                #print 'pillow has no source: ',self.id
                #Make line invisible by turnning it into a point 
                self.draw( (0,0,250), gpillow.rect.center, gpillow.rect.center)
                self.gunMachine.stop()
                self.gunMachine.update(pygame.time.get_ticks(), 0)
'''
    Mouse Controler: add functionality: drag,...
'''
class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        #self.image            = pygame.Surface([1,1])        
        #self.color            = (100,100,250)
        # Hack
        try: self.image = pygame.image.load('./data/hand_xs.png')
        except: 
            try: self.image = pygame.image.load('./MoveMe/MultiPillow/data/hand_xs.png')
            except: print "Error: Cannot find file hand_xs.png line 60 at Controllers.py"
            
        self.image.set_colorkey((0,0,0))
        self.rect             = self.image.get_rect()
        self.rect.center      = pygame.mouse.get_pos()
        self.next_update_time = 0 # update() hasn't been called yet.
        self.drag             = False
        self.buttons          = (0,0,0) 

        pygame.mouse.set_visible(False)
        #self.image.fill(self.color)
        
    def update(self, current_time, bottom,p):
        # Update every 10 milliseconds = 1/100th of a second.
        if self.next_update_time < current_time:          
            self.next_update_time = current_time + 10   
            self.rect.center     = pygame.mouse.get_pos()