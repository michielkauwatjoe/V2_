'''
Pillow is the class that will control a single pillow
'''
from StateMachine import *


class FIFO:
    def __init__(self):       
        self.__array = []
        self.__empty = True
        
    def get(self):
        if not self.__empty and self.__array:
            return self.__array.pop()
        else:
            return False
    
    def put(self,object):
        self.__empty = False
        self.__array.insert(0,object)
    
    def empty(self):
        self.__empty = True
        self.__array == []
    
    def isEmpty(self):
        return self.__empty or self.__array == []

    def getArray(self):
        return self.__array

'''
    Data structured used to store data from source pillow
'''
class Source(FIFO):
    def __init__(self):
        FIFO.__init__(self)
        self.__sourceId   = False  
        self.sourcePillow = False
                
    def setSourceId(self, id):
        self.__sourceId     = id
        #self.empty()  

    def getSourceId(self):
        return self.__sourceId

    def getSource(self):
        return self.get()

    def putSource(self, sourcePillow):
        pillow = Pillow()
        if sourcePillow.sourcePillow:
            # The source is an active pillow
            pillow = sourcePillow.sourcePillow.clone()   
            pillow.move.position = sourcePillow.move.position
        else:  
            # The source is an interactive pillow
            pillow = sourcePillow.clone()
        self.put(pillow)
        
    def emptySource(self):
        self.empty()  
        self.sourcePillow = False

    def lengthSource(self):
        return len(self.getArray())  
'''
    Pillow definition (or stateless pillow)
'''       
class Touch:
    def __init__(self):
        self.intensity = 0
        self.corners   = 0
        self.position  = (0,0)
        
    def touched(self):
        return self.intensity
    
    def clone(self):
        result = Touch()
        result.intensity = self.intensity
        result.position  = self.position
        return result
    
class Move:
    def __init__(self):
        self.position     = (0,0)
        self.velocity     = False
        self.acceleration = 0
        
    def moved(self):
        return self.velocity

    def clone(self):
        result = Move()
        result.position     = self.position
        result.velocity     = self.velocity
        result.accelaration = self.acceleration
        return result

class Pillow(Source):
    def __init__(self, id=0):
        Source.__init__(self)

        self.id      = id
        self.group   = 0
        self.name    = ''
                        

        self.color   = (250, 0, 0)
        self.beep    = {'volume':0,  'pitch':0, 'duration':0}
        self.touch   = Touch()
        self.move    = Move()
        

        self.now     = 0
        self.timeOut = 0
            
            
    def clone(self):
        result = Pillow()
        result.color = self.color
        result.touch = self.touch.clone()
        result.move  = self.move.clone()
        return result
           
                
    def setBeep(self, volume,  pitch, duration=20):
        self.beep = {'volume':volume,  'pitch':pitch, 'duration':duration}

    def getBeep(self):
        return self.beep

    def buzz(self, intensity, duration):
        pass

    def display(self, color):
        pass

'''
    Pillow extented with states
'''
class StatePillow(StateMachine, Pillow):
    def __init__(self, id=0):
        # Initalize Pillow
        Pillow.__init__(self, id)
        
        #
        self.delay      = 100
        self.stateDelay = 30000 #30 seconds
                
        # initialize state Machine 
        StateMachine.__init__(self) 
        self.addState("INACTIVE", self.inactiveState)
        self.addState("TOUCHED", self.touchedState)
        self.addState("MOVED", self.movedState)
        self.addState("ACTIVE", self.activeState)
        self.addState("END", None, end_state=1)           
        self.setStart("INACTIVE")

    
    def inactiveState(self):
        '''
            Inactive State:
        '''
        if self.state != self.prevState:
            print " *",self.name,"is inactive."
            self.state = 'INACTIVE'
            #self.color = (250, 250, 250)
            self.touch.intensity = 0
            self.setBeep(0,0,0) 
            
        # self.grayScale()
        
        ## Compute new state           
        if self.touch.touched():
            return "TOUCHED"
        elif self.move.moved():
            return "MOVED"
        elif self.getSourceId():
            return "ACTIVE"
        else:
            return "INACTIVE"
    
    def grayScale(self):
        inc = lambda x: int(x*0.0235)
        inc = lambda x: int(x*0.0235)
               
        if self.color[0] >= 255:
            pass
            
    def activeState(self):
        '''
            Active State:
        '''       
        if self.state != self.prevState:
            print ' *',self.name,'is active.'
            self.state = 'ACTIVE'
            self.consume  = False
        
        if self.consume or not self.getSourceId():
            ''' consume info from source '''
            self.sourcePillow = self.getSource()     
            #print 'consume ',self.sourcePillow  
        else:
            self.consume = self.lengthSource() > self.delay
                       
                       

        ''' Compute new state '''
        if self.touch.touched():
            return "MOVED"
        elif self.move.moved():
            return "TOUCHED"
        elif not self.sourcePillow and not self.getSourceId():
            # print 'INACTIVE --------------------------- ',self.sourcePillow
            return "INACTIVE"
        else:
            return "ACTIVE"
        
    
    def movedState(self):
        '''
            Moved State:
        '''         
        if self.state != self.prevState:
            print " *",self.name,"is moving."
            self.setSourceId(False)
            self.emptySource()            
            self.timeOut = self.now + self.stateDelay;
            self.state = 'MOVED' 
            #self.color = (0, 250, 0)
 
 
        ## Compute new state
        #if self.name == 'Soft(8)':
        #    print 'touched',self.timeOut ,'=', self.now
        
        if self.move.moved():
            self.timeOut = self.now + self.stateDelay;
            return "MOVED"   
        elif self.touch.touched():
            self.timeOut = self.now + self.stateDelay;
            return "TOUCHED"    
        elif self.timeOut > self.now:
            return "MOVED"
        else:
            return "INACTIVE"

    def touchedState(self):
        '''
            Touched State:
        '''
        if self.state != self.prevState:
            print " *",self.name,'is touched.'
            self.setSourceId(False)
            self.emptySource()
            self.state = 'TOUCHED'
            #self.color = (250, 0, 0)
            self.timeOut = self.now + self.stateDelay
            self.setBeep(100,100,2)


        ## Compute new state
        #if self.name == 'Soft(8)':
        #    print 'touched',self.timeOut ,'=', self.now
        
        if self.touch.touched():
            self.timeOut = self.now + self.stateDelay;
            return "TOUCHED"
        elif self.move.moved():
            self.timeOut = self.now + self.stateDelay;
            return "MOVED"
        elif self.timeOut > self.now:  
            return "TOUCHED"
        else:
            return "INACTIVE"
         


def main():
    pass
    
if __name__ == '__main__': main()