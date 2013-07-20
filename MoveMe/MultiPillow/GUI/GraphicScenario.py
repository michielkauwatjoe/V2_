import sys, pygame, random
from pygame.locals import *
from Shape import *
from Controllers import *
#from Room import *
#from Pillow import *
from MoveMe.MultiPillow.Room import *
from MoveMe.MultiPillow.Pillow import *

'''
    The graphic scenario contains the GUI to the pillows.
'''
class GraphicScenario:
    def __init__(self):
        pygame.init()
        # properties 
        self.room     = Room()
        self.inc      = 0
        self.pillows  = []  
        self.all      = pygame.sprite.RenderUpdates()
        
        #resolution = [848, 480]
        self.resolution = [1024, 640]
        
        # Create and add mouse listener to sprite
        self.mouse = Mouse()
        self.all.add(self.mouse)
        
        # Create Display
        self.createDisplay(self.resolution)
                
        # create some pillows
        for i in range(6):
            self.createPillow()

        # Add Bullet
        #self.bullet = Bullet()
        #self.all.add(self.bullet)
        
        # Create text
        self.text = self.createText()
        
        self.screen.blit(self.background, [0, 0])    
        pygame.display.flip()
        self.event = pygame.event.poll()
        self.key = ''

    def getInc(self):
        self.inc += 1
        return self.inc
    
    def createPillow(self):
        i = self.getInc()
        
        # Strange stuff to place pillows far from the borders
        xloc = self.resolution[0] - 100
        if self.resolution[0] < 100:
            xloc = 200
        yloc = self.resolution[1] - 100
        if self.resolution[1] < 100:
            yloc = 200
                        
        location = [ random.randrange(100, xloc)
                   , random.randrange(100, yloc)]
        gp = GraphicPillow(location, self.createShape(), i)
        print 'ok'
        gp.screen     = self.screen
        gp.background = self.background
        print 'end'
        
        self.all.add([gp,Line(i, self.screen)])
        self.pillows.append(gp)
        self.room.addPillow(gp.pillow)

    def createRealPillow(self):
        i = self.getInc()
        
        # Strange stuff to place pillows far from the borders
        xloc = self.resolution[0] - 100
        if self.resolution[0] < 100:
            xloc = 200
        yloc = self.resolution[1] - 100
        if self.resolution[1] < 100:
            yloc = 200
                        
        location = [ random.randrange(100, xloc)
                   , random.randrange(100, yloc)]
        gp = GraphicPillow(location, CircleGradient((0,0,250)), i)
        self.all.add([gp,Line(i)])
        self.pillows.append(gp)
        self.room.addPillow(gp.pillow)
        
        return len(self.pillows)
    
    def createShape(self):
        ''' Randomly choose a shape '''
        color = (0,0,250)  
        shape = {
          0: Donut(color,(120,80)),
          1: WormShape(color),
          2: TShape(color),
          3: PlusShape(color,(120,80)),
          4: TriShape(color),
          5: SixShape(color)         
        }[random.randrange(5)]
        return shape
    
    def createDisplay(self, resolution):
        # creat a window with a certain resolution
        self.screen = pygame.display.set_mode(resolution)
        # create a black surface of the window dimensions 
        self.background = pygame.Surface(resolution)
        self.background.fill([0, 0, 0])            
            
    def createText(self):
        
        pygame.display.set_caption('MoveMe simulator.')
        '''
        # Put Text On The Background, Centered
        if pygame.font:
            #font = pygame.font.Font('./data/DIRTYDOZ.TTF', 36)
            font = pygame.font.Font(None, 36)
            # print '******',pygame.font.get_fonts(),'******'
            text = font.render("MoveMe Prototype", 1, (250, 0, 0))
            textpos = text.get_rect(centerx=self.background.get_width()/2)
            # print textpos
            self.background.blit(text, textpos)
            return text
        '''
        
    def updateScreen(self):        
        # Save time by only calling this once
        # print pygame.time.get_ticks()
        self.all.update(pygame.time.get_ticks(), (self.mouse,self.key), self.pillows)
        rectlist = self.all.draw(self.screen)
        pygame.display.update(rectlist)
        pygame.time.wait(10)
        self.all.clear(self.screen, self.background)  

    def handleInput(self):  
        # enable window quit button 
        if self.event.type == pygame.QUIT: 
            sys.exit()

        # Mouse
        if self.event.type == MOUSEBUTTONUP:
            self.mouse.drag = False          
        elif self.event.type == MOUSEBUTTONDOWN:
            self.mouse.buttons = pygame.mouse.get_pressed()           
            self.mouse.drag = True
        else:
            self.mouse.buttons = (0,0,0)
                    
        # Keyboard
        if self.event.type == KEYDOWN:
            print self.event.unicode
            self.key = self.event.unicode
            
            # try to convert key to a number
            try:
                number = int(self.key)
                self.key = number
            except:
                pass
            
            # pressing g shows group formation
            if self.key == 'g':
                result = []
                for group in self.room.groups:
                    print group.pillows
                    print 'group (',group.id,')'
                    for pillowId in group.pillows:
                        pillow = group.pillows[pillowId]
                        result.append((pillow.id,pillow.getSourceId()))
                print result

            # pressing s shows pillows state
            if self.key == 's':
                for group in self.room.groups:
                    for pillow in group.pillows:
                        print pillow.id,'=',pillow.state

            # delete pillow
            group = self.room.groups[0]
            if group.pillows.has_key(self.key):
                pillow = group.pillows[self.key]
                print 'delete pillow ',pillow.id
                self.removePillow(self.key)
                
        else:
            self.key = ''
 
    def removePillow(self, pillowId):
        self.room.removePillow(pillowId)
        # get graphicalPillow
        gpillow = False
        
        for line in self.all:
            if line.__class__.__name__ == 'Line' and line.id == pillowId:
                line.kill()
                line.remove()
        
        for gp in self.pillows:
            if gp.pillow.id == pillowId:
                gpillow = gp
        if gpillow:
            gpillow.kill()
            gpillow.remove()
        
        
        
        
 
    def update(self):
        # 1) Update room
        self.room.run()
                
        # 2) Listen to user input.  
        self.handleInput()
        
        # 3) Update screen.
        self.updateScreen()
 
        # 4) Fetch new event.
        self.event = pygame.event.poll() 


'''
    GraphicPillow is the graphic represetation of a pillow. 
    The method update(time, mouse) is called periodically.
'''
class GraphicPillow(pygame.sprite.Sprite):
    def __init__(self, initial_position, shape, id=0):
        # extend sprite (sprites are periodically updated)
        pygame.sprite.Sprite.__init__(self)
        self.next_update_time = 0 # update() hasn't been called yet.        
        
        # This is the real pillow. This value should be read only.    
        self.pillow           = StatePillow(id)   
        self.color            = self.pillow.color

        # these proprieties are getting a bit messy
        self.shape            = shape
        self.image            = shape.image
        self.rect             = self.image.get_rect()
        self.rect.topleft     = initial_position
        self.offset           = (0,0)
        self.hand             = False
        self.drag             = False
        
        #self.image.fill(self.color)

    def showSource(self):
        pass


    def colorize(self):
        '''
            Approximates the color of a pillow to the argument color
            by incrementing or decrementing each color value by one 
            if self.color=(0,0,0) and self.newColor=(225,225,225) the result is (1,1,1)
        '''
        def adjust(sr, r):
            if   r>sr: sr+=1 
            elif r<sr: sr-=1
            return sr
                      
        #print 'colorize %s %s'%(self.color, self.pillow.color)
        self.color = map(adjust, self.color, self.pillow.color)
 
        self.image = self.shape.colorize(self.color)
          
        
    def update(self, current_time, (mouse, key), pillows):
        # Update every 10 milliseconds = 1/100th of a second.
        if self.next_update_time < current_time:
            self.next_update_time = current_time + 10 
                       
            # update color
            if tuple(self.color) != tuple(self.pillow.color):               
                self.colorize()
                
            # get mouse position
            mousePos = pygame.mouse.get_pos()

            # Mouse over test (moved or touched or none)                             
            mouseOver = self.rect.collidepoint(mousePos)
            
            if mouseOver and (mouse.buttons[2] or mouse.buttons[0]):
                self.offset = (self.rect.left-mousePos[0], self.rect.top-mousePos[1])
                print self.offset

            # update movement simulator
            #print mouseOver ,',', mouse.drag
            self.pillow.move.velocity = self.drag = mouseOver and mouse.drag
            # Move pillow along with mouse
            if self.drag:
                self.followMouse(mousePos)


            # Hand cursor
            if mouseOver and mouse.buttons[2]:
                print 'mouseOver and button2'
                if self.hand:
                    self.hand = False
                else:
                    self.hand = []
                    self.hand.append(mouse.image)
                    #self.hand.append((0,0))
                    self.hand.append((abs(self.offset[0])-12,abs(self.offset[1])-15))
                    print self.hand[1]
                    # this is not necessary
                    self.image.blit(self.hand[0], self.hand[1])

            # Show Master behaviour
 #           if False:
                if (mouseOver and not mouse.drag) or self.hand:
                    if tuple(self.color) == tuple(self.pillow.color): 
                        self.pillow.color = (self.pillow.color[1],self.pillow.color[2],self.pillow.color[0])
    
                    # Update Touch
                    self.pillow.touch.intensity = True 
                    self.pillow.touch.position  = (abs(self.offset[0]),abs(self.offset[1]))
                    self.shape.showTouch(self.pillow.touch.position, 10, (0,0,250))
                    # Not used
                    if key == 'c':
                        self.pillow.color = (self.pillow.color[1],self.pillow.color[2],self.pillow.color[0])           
                else:
                    self.pillow.touch.intensity = self.hand
                    #if self.pillow.touch.intensity > 0:
                    #    self.pillow.touch.intensity -= 100
          
            # Show Slave behaviour 
            if self.pillow.sourcePillow:
                if mouseOver and not mouse.drag:
                    print 'Warning: The pillow ',self.pillow.id ,' is touched and is a slave.'
                self.pillow.color = self.pillow.sourcePillow.color
                self.shape.showTouch(self.pillow.sourcePillow.touch.position, 10, (0,0,250))
                               
            if self.hand:
                self.image.blit(self.hand[0], self.hand[1])
                                  
            # Change pillow group
            # if mouseOver and key in range(0,10):
            #    self.group = key

    def visualizeTouch(self):
        pass

    def followMouse(self, (x, y)):
        #add offset to the mouse Pos
        self.rect.topleft = (x+self.offset[0],y+self.offset[1])



def main():
    graphicSce = GraphicScenario()
    
    while graphicSce.event.type != KEYDOWN:         
        graphicSce.update()
    
if __name__ == '__main__': main()