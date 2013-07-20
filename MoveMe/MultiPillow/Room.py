'''
Group is the class that will control a single group
'''
from StateMachine import *
from Pillow import *
import random 
import pygame

'''
'''
class Group(StateMachine):
    def __init__(self, id=0):
        self.id      = id
        self.pillows = {}
        self.color   = (250,250,250)
        self.nextUpdateTime = 0
        
        # StateMachine configuration ------------------------        
        StateMachine.__init__(self) 
        self.addState("INTERACTIVE", self.interactiveState)
        self.addState("INACTIVE", self.inactiveState)
        self.addState("ACTIVE", self.activeState)     
        self.setStart("INACTIVE")
        # ---------------------------------------------------
        
    def getSubStates(self):
        return self.pillows.itervalues()

    def inactiveState(self): 
        if self.state != self.prevState:
            ''' Run only when group just became inactive '''
            print "Group %s inactive"%self.id
        
        ''' If pillows become inactive change group color
            This should get out of here
        '''
        '''
        for pillow in self.pillows.itervalues():
            if self.id == 0:
                pillow.color = (0,250,250)
            elif self.id == 1:
                print 'here!!!!!!!!!!!!!!!!!!!!!'
                pillow.color = (250,250,250)
            elif self.id == 2:
                pillow.color = (250,0,250)
            elif self.id == 3:
                pillow.color = (125,250,0)
            elif self.id == 4:
                pillow.color = (0,125,250)
            elif self.id == 5:
                pillow.color = (0,125,125)
        '''                                        
        return self.newState()
            
       
    def activeState(self):
        if self.state != self.prevState:
            print "Group %s active"%self.id
                
        return "INACTIVE"
    
    
    def masters(self):
        '''
            A pillow is a master if it is interactive or has an interactive parent
        '''
        mastersID     = []
        newMastersID  = []
        ''' get inital masters '''
        for pillow in self.pillows.itervalues():
            if pillow.state == "TOUCHED" or pillow.state == "MOVED":
               mastersID.append(pillow.id) 
        

        if mastersID != []:
            oldMastersID = []
            newMastersID = mastersID
            while newMastersID != oldMastersID:
                oldMastersID = newMastersID
                newMastersID = self.tmpfunction(oldMastersID)
        
        return newMastersID
                 
    
    def tmpfunction(self,mastersID):
        for pillow in self.pillows.itervalues():
            if pillow.getSourceId() in mastersID and not pillow.id in mastersID:
               mastersID.append(pillow.id)
        return mastersID
    
    def getPillow(self, pillowId):
        result = False
        if pillowId in self.pillows.keys():
            result = self.pillows[pillowId]
        return result
        
    def interactiveState(self):
        ''' Only runs when pillows becames interactive '''
        if self.state != self.prevState:
            #print "Group %s interactive"%self.id
            pass
        ''' ----------------------------------- '''
        
        currentTime = pygame.time.get_ticks()
        
        if self.nextUpdateTime < currentTime:
            ''' Reorganize pillows dependencies '''
            masters = self.masters()
    
            if masters != []:
                ''' choose masters for slaves ''' 
                for pillow in self.pillows.itervalues():
                    if pillow.state == "INACTIVE":
                       ''' randomly choose a master '''
                       master = masters[random.randrange(len(masters))]
                       #print "master: ",master
                       pillow.setSourceId(master)
                       ''' add pillow to masters list '''
                       masters.append(pillow.id)
            
            ''' clean pillows with inactive sources '''
            for pillow in self.pillows.itervalues():
                sourceId = pillow.getSourceId() 
                ''' set source to false if source become INACTIVE or does not exist '''
                if sourceId:
                    if sourceId in self.pillows.keys():
                        source = self.pillows[sourceId]
                        if source.state == "INACTIVE":
                            pillow.setSourceId(False)
                    else:
                        pillow.setSourceId(False)

            self.nextUpdateTime = currentTime + 100
    
        ''' Feed slaves '''
        for pillow in self.pillows.itervalues():
            if pillow.getSourceId():
                #print 'pillow.getSource()=',pillow.getSource()
                if pillow.getSourceId() in self.pillows.keys():
                    pillow.putSource(self.pillows[pillow.getSourceId()])
                else:
                    pillow.setSourceId(False)
                
        return "INTERACTIVE"                                
        #return self.newState()



    def slavesCopyMasters(self,masters):
        ''' Slave pillows assume masters colors
            Here I should call all slave pillows 
        '''
        i = 0
        for pillow in self.pillows.itervalues():
            if pillow.state != "TOUCHED" and pillow.state != "MOVED":
                pillow.color =  masters[i].color
                if i  < len(masters):
                    i+=1
                else:
                    i=0  
            
    def newState(self):
        '''
        A group is interactive if one of its pillows is touched or moved.
        '''
        interactive = False
        for pillow in self.pillows.itervalues():
            interactive = interactive or pillow.state == "TOUCHED" or pillow.state == "MOVED"
            
        if interactive:
            return "INTERACTIVE"
        else:
            return "INACTIVE"


class Room(StateMachine):
    def __init__(self, groups=[]):
        self.groups = groups

        # StateMachine configuration ------------------------        
        StateMachine.__init__(self) 
        self.addState("INTERACTIVE", self.interactiveState)
        self.addState("INACTIVE", self.inactiveState)
        self.addState("ACTIVE", self.activeState)     
        self.setStart("INACTIVE")
        # ---------------------------------------------------
        self.createGroups()

    def addPillow(self, pillow):
        group = self.groups[0]
        print ' *',pillow.name,'added to Room.'
        group.pillows[pillow.id] = pillow 
    
    def removePillow(self, pillowId):
        group = self.groups[0]
        del group.pillows[pillowId] 

    def getPillow(self, pillowId):
        group = self.groups[0]
        return group.pillows[pillowId] 
        
    def addPillowToGroup(self, pillow, groupOld):
        print 'Remove pillow from original group'
        
        group = self.groups[groupOld]
        print 'here'
        #for pillow in group.pillows:
        #    print pillow.id
        del group.pillows[pillow.id]
        # Insert pillow in new group
        print self.groups
        print pillow.group
        newGroup = self.groups[pillow.group]
        newGroup.pillows[pillow.id] = pillow
        

    def createGroups(self):
        '''
            all pillows in 1 group.
        '''
        # Create two empty groups
        group = Group(1)
             
        # Add groups to the room
        self.groups.append(group)

  
    def updateGroups(self):
        # Optmize this!
        tmp = [] 
        for group in self.groups:
            for pillow in group.pillows.itervalues():
                if pillow.group != group.id:
                    print 'change pillow',pillow.id ,' to group ',group.id
                    tmp.append((pillow, group.id))
                    
        for p,id in tmp:
            self.addPillowToGroup(p, id)
        
    # StateMachine ------------------------------------------
    # So far, a Room is always in inactive state
    def getSubStates(self):
        return self.groups

    def inactiveState(self):
        #self.updateGroups()
        return "INACTIVE"
    def activeState(self):
        return "INACTIVE"
    def interactiveState(self):
        return "INACTIVE"
    # -------------------------------------------------------



def main():
    pass
    
if __name__ == '__main__': main()














































'''
    def createGroups_pairing(self, allPillows):
        # Create one group for each 2 pillows. 
        
        # Distribute available pillows in the groups
        t = 0
        i = 0    
        for gpillow in allPillows:
            if i == 0:
                print t,'group'
                tmpGroup = Group(t)
                tmpGroup.id = gpillow.pillow.group = t
                tmpGroup.pillows[gpillow.pillow.id] = gpillow.pillow
                i+=1
                t+=1
            else:
                gpillow.pillow.group = t-1
                tmpGroup.pillows[gpillow.pillow.id] = gpillow.pillow
                self.groups.append(tmpGroup)
                i=0
            

        for group in self.groups:
            print 'groupp ',group.id
        
    def createGroups_twoGroups(self, allPillows):
        #Divide all pillows into 2 groups.
        
        # Create two empty groups
        group1 = Group(1)
        group2 = Group(2)    
        
        # Distribute available pillows in the groups
        i = 0;    
        for gpillow in allPillows:
            if i < 5:
                # print 'pilllow ',i,' in group',group1.id
                group1.pillows.append(gpillow.pillow) 
            else:
                # print 'pilllow ',i,' in group',group2.id
                group2.pillows.append(gpillow.pillow) 
            i+=1
    
        # Add groups to the room
        self.groups.append(group1)
        self.groups.append(group2)
        
'''