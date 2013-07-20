'''
abstract state machine from:
http://www-128.ibm.com/developerworks/library/l-python-state.html
'''
from string import upper


class StateMachine:
    def __init__(self):    
        self.state      = None
        self.prevState  = None             
        self.startState = None
        self.endStates  = []        
        self.handlers   = {}
        
    def addState(self, name, method, end_state=0):
        name = upper(name)
        self.handlers[name] = method
        if end_state:
            self.endStates.append(name)

    def setStart(self, name):
        self.startState = upper(name)
        self.state = upper(name)

    def getSubStates(self):
        return []

    def run(self):
        # run all possible substates
        for substate in self.getSubStates():
            substate.run()        
         
        # if self.prevState != self.state:
        #    print self.state #,' ',self.handlers
        
        # apply self state
        #TODO: apply is deprecated, Use the extended call syntax instead
        #print self.state,' ',self.handlers
        resState = apply(self.handlers[self.state])
        self.prevState = self.state
        self.state = upper(resState)        
        
        
        
        
        
        
        
        
        
        

class StateMachine_OLD:
    def __init__(self):
        self.handlers   = {}
        self.startState = None
        self.endStates  = []

    def addState(self, name, handler, end_state=0):
        name = upper(name)
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def setStart(self, name):
        self.startState = upper(name)

    def run(self, scenario):
        #
        try:
            print scenario.pillows.sprites
            for gpillow in scenario.pillows:
                gpillow.pillow.handler = self.handlers[self.startState]
        except:
            raise "InitializationError", "must call .setStart() before .run()"
      
        if not self.endStates:
            raise "InitializationError", "at least one state must be an endState"

     
        while 1:
            scenario.update()
            
            for gpillow in scenario.pillows:
                cargo = gpillow.pillow

                #print "pillow: %s, %s, %s, %s"%(cargo.state,cargo.moved, cargo.touched, cargo.quiet)
                (newState, cargo) = gpillow.pillow.handler(cargo)
                
                if upper(newState) in self.endStates:
                    break
                else:
                    gpillow.pillow.handler = self.handlers[upper(newState)]  