#import pygame and the system library
import sys, pygame
from pygame.locals import *
#from Pillow import *
from MoveMe.MultiPillow.Pillow import *

class Circle(pygame.sprite.Sprite):
    def __init__(self, orig, color=(255,0,0), radius=50, width=0):
        pygame.sprite.Sprite.__init__(self)
        ''' Create surface '''
        self.image  = pygame.Surface((2*radius, 2*radius))
        self.rect   = self.image.get_rect()
        self.image.set_colorkey((0,0,0))
        self.rect.center = orig
        self.radius = radius
        #self.color  = color
        #self.image.set_alpha(100)
        ''' Draw shape '''
        pygame.draw.circle(self.image, color, (self.radius,self.radius), self.radius)

    def reDraw(self,color):
         pygame.draw.circle(self.image, color, (self.radius,self.radius), self.radius)
                
class GraphicPillow(Circle):
    ''' Pillow graphical representation ''' 
    def __init__(self, id, group, orig=(0,0)):
        self.nextUpdateTime = 0
        self.__id = id
        Circle.__init__(self, orig)
        
        ''' Add yourself to render group '''
        self.group = group
        self.group.add(self)
        
        self.statePillow = StatePillow(id)
        self.statePillow.move.position = orig
        ''' Add a spriteMachine '''
        self.spriteMachine = SpriteMachine(self.group, (0,0), (0,0), 0)
        
        self.drag      = False 
        self.mouseOver = False
        self.offset    = (0,0)
        self.color     = (250,250,250)
        
    def getId(self):
        return self.__id 
    def update(self, currentTime, mouse):
        if self.nextUpdateTime < currentTime:
            self.nextUpdateTime = currentTime + 10 
            
        ''' Mouse over test (moved or touched or none) '''                      
        self.mouseOver = self.rect.collidepoint(mouse.position)


        ''' 0) Slave behaviour '''
        if self.statePillow.sourcePillow: self.slaveBehaviour(mouse)
        ''' 1) Update color '''
        self.colorize()        
        ''' 2) Check for movement'''
        self.movement(mouse)
        ''' 3) Check for touch'''
        self.touch(mouse)

    def slaveBehaviour(self, mouse):
        if self.mouseOver and not mouse.drag:
            print 'Warning: The pillow ',self.statePillow.id ,' is touched and is a slave.'
        
        self.statePillow.color = self.statePillow.sourcePillow.color
        # self.shape.showTouch(self.statePillow.sourcePillow.touch.position, 10, (0,0,250))
        ''' show connection '''
        # print self.statePillow.sourcePillow.move.position, self.statePillow.move.position
        self.spriteMachine.shotSprite( self.statePillow.sourcePillow.move.position
                                     , self.statePillow.move.position
                                     , self.statePillow.sourcePillow.color
                                     )
        
                            
    def colorize(self):
        '''
            Approximates the color of a pillow to the argument color
            by incrementing or decrementing each color value by one 
            if self.color=(0,0,0) and self.newColor=(225,225,225) the result is (1,1,1)
        '''
        if tuple(self.color) != tuple(self.statePillow.color):
            def adjust(sr, r):
                if   r>sr: sr+=1 
                elif r<sr: sr-=1
                return sr
                          
            #print 'colorize %s %s'%(self.color, self.pillow.color)
            self.color = map(adjust, self.color, self.statePillow.color)
            self.reDraw(self.color)
            
    def touch(self, mouse):
        ''' Simulate 4 corner touch '''
        if self.mouseOver and not mouse.drag:
            self.statePillow.touch.intensity = 1
            if mouse.position[0] > self.rect.left + self.rect.width / 2:
                if mouse.position[1] > self.rect.top + self.rect.height / 2:
                    self.statePillow.touch.corners = 4
                else:
                    self.statePillow.touch.corners = 2
            else:
                if mouse.position[1] > self.rect.top + self.rect.height / 2:
                    self.statePillow.touch.corners = 3
                else:
                    self.statePillow.touch.corners = 1
        else:
            self.statePillow.touch.intensity = 0
            
    def movement(self, mouse):
        if mouse.drag:
            # mouse dragged for the first time
            if self.mouseOver and (mouse.buttons[2] or mouse.buttons[0]):
                self.offset = (self.rect.left-mouse.position[0], self.rect.top-mouse.position[1])
                # print 'offset',self.offset

            ''' update movement simulator '''
            self.statePillow.move.velocity = self.drag = self.offset[0]+self.offset[0] != 0

            ''' Move pillow along with mouse '''
            if self.drag:
                self.followMouse(mouse.position)
                self.statePillow.move.position = self.rect.center
        else:
            self.offset = (0,0)
            self.statePillow.move.velocity = 0
            
    def followMouse(self, (x, y)):
        ''' add offset to the mouse Pos '''
        self.rect.topleft = (x+self.offset[0],y+self.offset[1])




    def remove(self):
        self.spriteMachine.kill()
        self.kill()

class MotionSprite:
    def __init__(self, initialPosition, finalPosition, speed = 1):
        '''update() hasn't been called yet. '''
        self.next_update_time = 0 

        self.rect.center     = initialPosition
        self.speed           = speed

        self.orig = initialPosition
        self.dest = finalPosition
        ''' exact position (float) '''
        self.position = initialPosition

        self.incSize = 1
        self.inc = (1,1)
        self.calculateInc()
        
    def calculateInc(self):
        ''''''
        dist = ( self.dest[0]-self.orig[0]
               , self.dest[1]-self.orig[1]
               )
        
        maxDistance = abs(float(max(dist)))

        #self.incSize = maxDistance/self.rect.width
        #print 'aaaa',self.incSize
        self.incSize = 1
        
        if maxDistance != 0:
            self.inc   = ( dist[0]/maxDistance*self.speed
                         , dist[1]/maxDistance*self.speed
                         )
        else:
            # print self.dest
            if dist[0] == 0:
                if dist[1] < 0: v = -1 
                else: v = 1
                self.inc   = ( 0, v*self.speed)
            else:
                if dist[0] < 0: v = -1 
                else: v = 1
                self.inc   = (v*self.speed, 0)

        #print self.inc

    def move(self):
        ''' exact position (float) '''
        self.position = ( self.position[0] + self.inc[0]
                        , self.position[1] + self.inc[1]
                        )
        ''' round position (int) '''
        self.rect.center = self.position
        self.radius += self.incSize
        alpha=self.image.get_alpha()
        if alpha == None: alpha = 0 
        self.image.set_alpha(alpha+self.speed)
        self.reDraw(self.color)
        #self.setAlpha(self.alpha)
        #self.size  += self.inc[0]
                    
    def update(self, current_time, newDest):
        ''' '''
        if self.next_update_time < current_time:
            self.next_update_time = current_time + 10
            
            ''' code for variable destination '''
            #if newDest != self.dest:
            #    self.dest = newDest
            #    self.calculateInc()
            
            ''' Test if sprite arrived to destination '''
            arrived = (self.inc[0] > 0 and self.rect.center[0] > self.dest[0] or 
                       self.inc[0] < 0 and self.rect.center[0] < self.dest[0] or
                       self.inc[1] > 0 and self.rect.center[1] > self.dest[1] or 
                       self.inc[1] < 0 and self.rect.center[1] < self.dest[1] 
                       )
            
            # print 'done',done
            if  not arrived:       
                self.move()
            else:
                # print 'sprite killed'
                self.kill()
                #self.bounce()

    def bounce(self):
        ''' Bounce '''
        tmp = self.orig
        self.orig = self.dest
        self.dest = tmp
        ''' exact position (float) '''
        self.position = self.orig

        # self.inc = (-1*self.inc[0],-1*self.inc[1])
        self.calculateInc()
        # print self.orig, self.position, self.dest, self.inc
        # self.move()         


        
class Rect(MotionSprite,pygame.sprite.Sprite):
    def __init__(self, color, initialPosition, finalPosition, size =(15,15), speed = 1):
        pygame.sprite.Sprite.__init__(self)
        ''' Create surface '''
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect()
        ''' Create Shape '''
        self.image.fill(color)
        ''' Extend Motion '''
        MotionSprite.__init__(self, initialPosition, finalPosition, speed)
 #   def update(self, current_time, bottom):
 #       self.move(current_time, bottom)
                
class MotionCircle(MotionSprite, pygame.sprite.Sprite):
    def __init__(self, color, radius, width, initialPosition, finalPosition, speed = 5):
        pygame.sprite.Sprite.__init__(self)
        ''' Create surface '''
        self.image = pygame.Surface((2*radius, 2*radius))
        self.rect  = self.image.get_rect()
        self.image.set_colorkey((0,0,0))
        self.image.set_alpha(0)
        self.radius = 1     
        self.color  = color  
        ''' Draw shape '''
        pygame.draw.circle(self.image, color, self.rect.center, radius)
        ''' Extend Motion '''
        MotionSprite.__init__(self, initialPosition, finalPosition, speed)
 

    def reDraw(self,color):
        pass
        '''
        print self.radius
        newImage = pygame.Surface((30, 30))
        pygame.draw.circle(newImage, (255,0,0), self.rect.center, self.radius)
        self.image = newImage
        '''
        
#    def update(self, current_time, bottom):
#        self.move(current_time, bottom)        
                        
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, images, fps = 10):
        pygame.sprite.Sprite.__init__(self)
        self._images = images

        ''' Track the time we started, and the time between updates.
            Then we can figure out when we have to switch the image. 
        '''
        self._start = pygame.time.get_ticks()
        self._delay = 1000 / fps
        self._last_update = 0
        self._frame = 0

        ''' Call update to set our first image. '''
        self.update(pygame.time.get_ticks())

    def update(self, t):
        ''' Note that this doesn't work if it's been more that self._delay
            time between calls to update(); we only update the image once
            then, but it really should be updated twice.
        '''

        if t - self._last_update > self._delay:
            self._frame += 1
            if self._frame >= len(self._images): self._frame = 0
            self.image = self._images[self._frame]
            self._last_update = t


class SpriteMachine(pygame.sprite.Sprite):
    def __init__(self, group, orig, dest, color = (255, 0, 0), spritesNum=0, speed=250):
        ''' This is a faked sprit'''
        self.image = pygame.Surface((0,0))
        #self.image.fill((0,0,0))
        self.rect         = self.image.get_rect()
        self.rect.center  = orig
        pygame.sprite.Sprite.__init__(self)
        self.next_update_time = 0 
        ''' '''
        self.dest       = dest
        self.orig       = orig
        self.dest       = dest
        self.group      = group
        # number of seconds until next sprite is created
        self.speed      = speed
        self.color      = color
        self.spritesNum = spritesNum
        ''' Add yourself to group '''
        group.add(self)

    def shotSprite(self, orig, dest, color):
        self.spritesNum = 2
        self.orig  = orig
        self.dest  = dest
        self.color = color
        
    def addSprite(self):
        if self.spritesNum > 0:
            self.spritesNum -= 1
            self.group.add(MotionCircle(self.color, 10, 0, self.orig, self.dest))
            
    def update(self, current_time, var):
        ''' '''
        if self.next_update_time < current_time:
            self.next_update_time = current_time + self.speed
            
            self.addSprite()