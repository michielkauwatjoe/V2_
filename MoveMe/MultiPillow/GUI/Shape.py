#import pygame and the system library
import sys, pygame
from pygame.locals import *

from gradients import gradient

class Shape:
    def __init__(self, shape, color):
        self.shape = shape
        self.shape.set_colorkey(color)
        self.__color = color
            
        self.image = pygame.Surface(self.shape.get_size())
        self.image.set_colorkey((0,0,0))
        self.image.fill(color)
        self.image.blit(self.shape, (0,0))    

    def colorize(self, color):
        self.__color = color
        self.image.set_colorkey((0,0,0))
        self.image.fill(color)
        self.image.blit(self.shape, (0,0))
        return self.image
    
    
    def showTouch(self,offset,radius,color):
        #print 'colorize'
        if radius == 0:
            radius == 1
 
        # used to clean previous stuff
        self.colorize(self.__color)
                    
        for inc in [18,15,12,9,3]:
        # -----
            self.blur = pygame.Surface(self.shape.get_size())   
            self.blur.set_colorkey((0,0,0))
            newRadius = radius+inc-3
            pygame.draw.ellipse(self.blur, color, Rect(offset[0]-newRadius/2, offset[1]-newRadius/2,newRadius,newRadius))      
            self.blur.set_alpha(inc*7)
            self.blur.blit(self.shape, (0,0))
            self.image.blit(self.blur, (0,0))        
        # -----
            

        #pygame.draw.ellipse(self.image, color, Rect(offset[0]-radius/2, offset[1]-radius/2,radius+5,radius+5))
        #self.image.set_alpha(200)
        #self.image.blit(self.shape, (0,0))        
        pygame.draw.ellipse(self.image, color, Rect(offset[0]-radius/2, offset[1]-radius/2,radius,radius))
        #self.image.set_alpha(200)
        self.image.blit(self.shape, (0,0))  
 
 

 
        
    def resize(self, size):
        pass

#
# Shape Examples
#
class LineShape(Shape):
    def __init__(self, color=(120,120,120), org=(0,0), dest=(5,5)):
        size=(abs(org[0]-dest[0])+1,abs(org[1]-dest[1])+1)
        self.shape = pygame.Surface(size)
        
        pygame.draw.aaline(self.shape, color, org, dest)
        #pygame.draw.ellipse(self.shape, color, (size[0]/2,size[1]/2,5+size[0]/2,5+size[1]/2) )
        Shape.__init__(self, self.shape, color)

    def draw(self, color, org, dest):
        size=(abs(org[0]-dest[0])+1,abs(org[1]-dest[1])+1)
        #size=(1024,640)
        self.shape = pygame.Surface(size)
        
        # position surface
        minX,minY = (min(org[0],dest[0]),min(org[1],dest[1]))
        self.rect.topleft = (minX,minY)
        
        # draw line
        pygame.draw.aaline(self.shape, color, (abs(org[0]-minX),abs(org[1]-minY)), (abs(dest[0]-minX),abs(dest[1]-minY)))
        Shape.__init__(self, self.shape, color)

class CircleGradient(Shape):
    def __init__(self, color=(255,0,0,255), radius=50):
        self.drawCircle(color, radius)

    def drawCircle(self, color=(255,0,0,255), radius=50):
        self.shape = pygame.Surface((radius*2,radius*2))
        self.radius = radius
        pygame.draw.circle(self.shape, color, (radius,radius), radius, 4)
        # Create circle using gradient
        '''
        gradient(self.shape
                , (radius,radius)
                , (radius,radius*2)
                , (color[0],color[1],color[2],100)
                , (0,0,0,255)
                #, (color[0],color[1],color[2],0)
                ,(lambda x:x), (lambda x:x), (lambda x:x), (lambda x:x) , "circle")
        '''
        Shape.__init__(self, self.shape, color)
        self.image.set_alpha(100)
        #pygame.draw.circle(self.image, color, (radius,radius), radius, 3)
        


    def colorize(self, color):
        self.drawCircle(color, self.radius)
        
        return self.image

    def setAlpha(self, value):
        self.image.set_alpha(value)

    def draw(self, color, radius=-1):
        if radius > 0:
            self.radius = radius
    
        self.drawCircle(color, self.radius)


class Circle(Shape):
    def __init__(self, color=(0,0,0), size=(100,100)):
        self.shape = pygame.Surface(size)
        
        pygame.draw.ellipse(self.shape, color, Rect(0, 0, size[0], size[1]))
        Shape.__init__(self, self.shape, color)
        
    def setAlpha(self, value):
        self.image.set_alpha(value)

    def draw(self, color, size=(50,50)):
        # print 'sssssssssssssssssssssss',size
        if size[0] > 0 and size[1] > 0: 
            self.shape = pygame.Surface(size)
            pygame.draw.ellipse(self.shape, color, Rect(0, 0, size[0], size[1]))
            Shape.__init__(self, self.shape, color)


class Donut(Shape):
    def __init__(self, color=(0,0,0), size=(120,80), width=50):
        self.shape = pygame.Surface(size)
        self.width = width
        pygame.draw.ellipse(self.shape, color, Rect(0, 0, size[0], size[1]))
        pygame.draw.ellipse(self.shape, (0,0,0), Rect(10, 10, size[0]-self.width, size[1]-self.width))
        Shape.__init__(self, self.shape, color)
        
    def setAlpha(self, value):
        self.image.set_alpha(value)

    def draw(self, color, size=(120,80)):
        # print 'sssssssssssssssssssssss',size
        if size[0] > 0 and size[1] > 0: 
            self.shape = pygame.Surface(size)
            pygame.draw.ellipse(self.shape, color, Rect(0, 0, size[0], size[1]))
            pygame.draw.ellipse(self.shape, (0,0,0), Rect(10, 10, size[0]-20, size[1]-20))
            Shape.__init__(self, self.shape, color)

            

class LengthShape(Shape):
    def __init__(self, color=(0,0,0), size=(155,50)):
        self.shape = pygame.Surface((155, 50))
        
        pygame.draw.ellipse(self.shape, color, Rect(00, 0, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(35, 0, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(70, 0, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(105,0, 50, 50))
        Shape.__init__(self, self.shape, color)



class WormShape(Shape):
    def __init__(self, color=(0,0,0), size=(155,50)):
        self.shape = pygame.Surface((155, 60))
        
        pygame.draw.ellipse(self.shape, color, Rect(00, 00, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(30, 05, 40, 40))
        pygame.draw.ellipse(self.shape, color, Rect(55, 10, 30, 30))
        pygame.draw.ellipse(self.shape, color, Rect(75, 15, 20, 20))
        Shape.__init__(self, self.shape, color)

class PlusShape(Shape):
    def __init__(self, color=(0,0,0), size=(80, 80)):
        
        self.shape = pygame.Surface(size)
        self.shape.set_colorkey(color)
        pygame.draw.ellipse(self.shape, color, Rect(0, 20, 80, 40))
        pygame.draw.ellipse(self.shape, color, Rect(20, 0, 40, 80))
        
        Shape.__init__(self, self.shape, color)
        #self.image = pygame.Surface(__size)

class TShape(Shape):
    def __init__(self, color=(0,0,0), size=(80, 80)):
        
        self.shape = pygame.Surface(size)
        self.shape.set_colorkey(color)
        pygame.draw.ellipse(self.shape, color, Rect(0, 20, 80, 40))
        pygame.draw.ellipse(self.shape, color, Rect(0, 0, 40, 80))
        
        Shape.__init__(self, self.shape, color)


class TriShape(Shape):
    def __init__(self, color=(0,0,0), size=(80, 80)):
        
        self.shape = pygame.Surface(size)
        self.shape.set_colorkey(color)
        pygame.draw.ellipse(self.shape, color, Rect(30, 30, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(00, 30, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(15, 00, 50, 50))
        Shape.__init__(self, self.shape, color)


class SixShape(Shape):
    def __init__(self, color=(0,0,0), size=(120, 120)):
        
        self.shape = pygame.Surface(size)
        self.shape.set_colorkey(color)
        pygame.draw.ellipse(self.shape, color, Rect(20, 00, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(00, 20, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(00, 40, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(40, 20, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(40, 40, 50, 50))
        pygame.draw.ellipse(self.shape, color, Rect(20, 60, 50, 50))
        Shape.__init__(self, self.shape, color)


class AmorphShape(Shape):
    def __init__(self, color=(0,0,0), size=(80, 60)):        
        amorph = pygame.Surface((90, 64))
        pygame.draw.ellipse(amorph, color, Rect(4, 10, 80, 50))
        pygame.draw.ellipse(amorph, color, Rect(0, 0, 50, 60))
        Shape.__init__(self, amorph, color)



        
'''
    GunMachine a sprite.group of bullets
'''
class GunMachine(pygame.sprite.RenderUpdates):
    def __init__(self, screen, background, orig=(0,0), dest=(400,400), color=(250,0,0), shots=10):
        #pygame.sprite.Sprite.__init__(self)        
        # group properties
        
        self.screen=screen
        print 'background',background
        self.background=background
        
        self.orig=orig
        self.dest=dest
        self.color = color
        self.shots = 10
        #
        self.next_update_time = 0
        self.speed = 250
        # Extend Sprite 
        pygame.sprite.Group.__init__(self)
        
    def stop(self):
        self.shots = 0
        
    def addShots(self,orig=(0,0), dest=(400,400), color=(250,0,0), inc=1):
        self.orig=orig
        self.dest=dest
        self.color = color        
        self.shots+=inc
        
    def update(self, current_time, other):
        #self.background.fill((255,255,255))
        self.clear(self.screen, self.screen)  
        pygame.sprite.Group.update(self, current_time, other)
        
        if self.next_update_time < current_time:
            # Add another bullet
            if self.shots > 0:   
                print 'Shoot 1 bullet for every ',self.speed,'ms.',self.color
                bullet = Bullet(self.orig, self.dest, self.color)
                self.add(bullet)
                self.shots-=1
                
            # Update timer
            self.next_update_time = current_time + self.speed
        
        rectlist = self.draw(self.screen)
        pygame.display.update(rectlist)
        #self.draw(self.screen)
        


'''
    Bullet Controler: creates a circle at orig and makes it move to dest 
                      and then disappears.
'''
class Bullet(pygame.sprite.Sprite, CircleGradient):
    def __init__(self, orig=(0,0), dest=(400,400), color=(250,0,0)):
        # Extend Sprite 
        pygame.sprite.Sprite.__init__(self)
        self.next_update_time = 0 # update() hasn't been called yet.
         
        # Extend CircleGradient Shape
        CircleGradient.__init__(self, color, 10)
        print 'radius',self.radius
        # bullet proprieties 
        print 'orig = ',orig
        print 'dest = ',dest
        self.orig   = orig
        self.dest   = dest
        self.color  = color
               
        # posi
        self.rect             = self.image.get_rect()
        print self.rect.topleft,' = ',
        print self.orig
        self.rect.topleft     = self.orig

        self.inc = (5,5)
        self.speed(15)
        
    def speed(self, speed):
        dist = ( self.dest[0]-self.orig[0]
               , self.dest[1]-self.orig[1]
               )

        minDistance = abs(float(min(dist)))

        if minDistance != 0:
            self.inc   = ( int(dist[0]/minDistance*speed)
                         , int(dist[1]/minDistance*speed)
                         )
        print self.inc
    
    def move(self):
          self.rect.topleft = ( self.rect.topleft[0] + self.inc[0]
                              , self.rect.topleft[1] + self.inc[1]
                              )             
          #self.alpha += self.inc[0] 
          #self.setAlpha(self.alpha)
          #self.size  += self.inc[0]

          #self.draw(self.color)
                    
    def update(self, current_time, bottom):
        ''' '''
        #print self.rect.topleft[0],'<',self.dest[0],']]',self.inc[0]
        done = (self.inc[0] > 0 and self.rect.topleft[0] > self.dest[0] or 
               self.inc[0] < 0 and self.rect.topleft[0] < self.dest[0])
        
        #print 'done',done
        
        if self.next_update_time < current_time and not done:       
            self.move()
            # Update timer
            self.next_update_time = current_time
        else:
            self.kill()
            
            
            
        

        
# -----------------------------------------------------------------------------
# Only for testing purposes
# -----------------------------------------------------------------------------  
        
class Scenario:
    def __init__(self):
        pygame.init() 
        
        # set the window properties
        self.size   = (600,600)
        
        self.background = pygame.Surface(self.size)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption('Shapes playground.')
        
        self.event  = pygame.event.poll()
        
        
        # init gunMachine
        self.gunMachine = GunMachine(self.screen, self.background,(0,300),(400,0))
        
        # init bullet
        self.bullet = Bullet((50,50), (400,400), (250,0,0))    
        self.screen.blit(self.bullet.image, (50,50))  
              
    def update(self):
        # enable window quit button 
        if self.event.type == pygame.QUIT: sys.exit()


        # clean screen
        
        black = (0,0,0)
        
        self.screen.fill((255,255,255))
        
        # draw new circle        
        color = (50, 220, 100)        
        red, green, blue = ((250,0,0), (0,250,0), (0,0,250))
        
        # circle follows mouse
        radius = 8
        self.circle = pygame.Surface((2*radius,2*radius))
        #self.circle.set_alpha(0) 
        pygame.draw.circle(self.circle, color, (radius,radius), radius)
        self.screen.blit(self.circle, pygame.mouse.get_pos())  
        
        
     
        self.bullet.update(pygame.time.get_ticks(), 0)   
        self.screen.blit(self.bullet.image, self.bullet.rect)  

         
        circleGradient = CircleGradient((250,0,250), 25)
        circleGradient.colorize((250,250,0))        
        self.screen.blit(circleGradient.image, (300,300))
             
        #amorph = AmorphShape((250,0,250))    
        #self.screen.blit(amorph.image, (0,0)) 

        #plusShape
        plusShape = PlusShape((255,255,255))
        self.screen.blit(plusShape.image, (150,150))


        #Donut
        donut = Donut((250,0,0),(120,80))
        donut.image.set_alpha(50)
        self.screen.blit(donut.image, (100,100))
        
        # Mouse over test (moved or touched or none)
        mousePos   = pygame.mouse.get_pos()                       
        donut.rect = donut.image.get_rect()
        donut.rect = Rect(donut.rect.left+100,donut.rect.top+100,donut.rect.width,donut.rect.height)         
        mouseOver  = donut.rect.collidepoint(mousePos)
        
        if mouseOver:
            donut.offset = (donut.rect.left-mousePos[0], donut.rect.top-mousePos[1])
            donut.showTouch((abs(donut.offset[0]),abs(donut.offset[1])),20,(0,100,200))
            self.screen.blit(donut.image, (100,100))
            print donut.offset
        
        
        color=(250,250,0)
        radius = 20
        for inc in [18,15,12,9,3]:
        # -----
            blur = pygame.Surface((100,100))   
            blur.set_colorkey((0,0,0))
            newRadius = radius+inc
            #pygame.draw.ellipse(blur, color, Rect(offset[0]-newRadius/2, offset[1]-newRadius/2,newRadius,newRadius))   
            pygame.draw.circle(blur, color, (radius,radius),radius)      
            blur.set_alpha(200-inc*10)  
            print 'alpha',200-inc*10
            self.screen.blit(blur, (300,100))                 
        '''        
        '''       
        
        # ooo-shape
        worm = WormShape(((0,0,250)))
        worm.colorize(black)
        #worm.showTouch((50,50))
        
        self.screen.blit(worm.image, (0,200))


        self.gunMachine.update(pygame.time.get_ticks(), 0)
        #pygame.display.update(rectlist)
        #self.screen.blit(self.bullet.image, self.bullet.rect.topleft)
                
                
        # update display
        pygame.display.update()
        # delay 
        pygame.time.delay(100)
        self.event = pygame.event.poll()

def main():
    virtualSce = Scenario()
    
    while virtualSce.event.type != KEYDOWN:         
        virtualSce.update()
        
if __name__ == '__main__': main()       










'''
    Bullet Controler
'''
class Bullet2(pygame.sprite.Sprite, Circle):
    def __init__(self, pos=(0,0), dest=(400,400), color=(250,0,0)):
        # Extend Sprite 
        pygame.sprite.Sprite.__init__(self)
        self.next_update_time = 0 # update() hasn't been called yet.
        
 
        # Extend Circle Shape
        Circle.__init__(self, (250,0,0))

        
        # bullet proprieties 
        self.pos    = pos
        self.dest   = dest
        self.color  = (100,100,250)
        self.alpha  = 255
        self.incX   = 0
        self.incY   = 0
        self.size   = 50
       
        # Speed calculation ------------------------ 
        self.speed()
         
        # posi
        self.rect             = self.image.get_rect()
        self.rect.topleft     = self.pos


    def speed(self):
        xDistance   = self.dest[0]-self.pos[0]
        yDistance   = self.dest[1]-self.pos[1]
        maxDistance = max(xDistance, yDistance)

        if maxDistance != 0:
            self.incX   = xDistance/maxDistance
            self.incY   = yDistance/maxDistance
        
        if xDistance < 0:
            self.incX = self.incX*-1
        if yDistance < 0:
            self.incY = self.incY*-1
                   
        print '(',self.incX,',',self.incX,')'
    
    def shoot(self):
          self.rect.topleft = ( self.rect.topleft[0] + self.incX
                            , self.rect.topleft[1] + self.incY
                            )             
          self.alpha += self.incX 
          self.setAlpha(self.alpha)
          self.size  += self.incX
          self.draw(self.color, (self.size, self.size))
          #pygame.transform.scale2x(self.image)
          # 
          
    def update(self, current_time, bottom):
        # Update every 10 milliseconds = 1/100th of a second.
        #print self.incX,' > 0 and', self.rect.topleft[0],' > ',self.dest[0]
        
        done = self.incX > 0 and self.rect.topleft[0] > self.dest[0] or self.incX < 0 and self.rect.topleft[0] < self.dest[0]
        
        if self.next_update_time < current_time and not done:            
            self.shoot()
  
            # Update timer
            self.next_update_time = current_time + 10   

