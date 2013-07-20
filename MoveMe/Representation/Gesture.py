class Normalize:
    ''' normalizes a value into values in the interval [0,1]'''
    def __init__(self):
        self.raw  = None
        self.min  = None
        self.max  = None
        self.norm = None
        
    def update(self, val):
        if val != self.raw:
            self.raw = round(val,5)
            if   self.raw > self.max: self.max = self.raw
            elif self.raw < self.min: self.min = self.raw
            
            if self.min == None:
                self.min = self.raw
            
            if (self.max-self.min) == 0:
                self.norm = 1.
                if self.max == 0: self.norm = 0.
            else:
                self.norm = round((val-self.min)/float(self.max-self.min), 5)

    def show(self):
        result = self.norm, self.min, self.max, self.raw
        return result

class RealTime:
    ''' normalizes gesture input into values in the interval [0,1]'''
    def __init__(self):
        self.area      = Normalize()
        self.intensity = Normalize()
        
    def update(self, gestureInput):
        self.area.update(gestureInput.realtime_intensity)
        self.intensity.update(gestureInput.realtime_area)
        
    def show(self, verbose = True):
        print 'Area      = ',self.area.show()
        print 'Intensity = ',self.intensity.show()

class Gesture:
    ''' normalizes gesture input into values in the interval [0,1]'''
    def __init__(self):
        self.area     = Normalize()
        self.time     = Normalize()
        self.space    = Normalize()
        self.intensity= Normalize()

    def update(self, gestureInput):
        self.area.update(gestureInput.numeric_values['area'])
        self.time.update(gestureInput.numeric_values['time'])
        self.space.update(gestureInput.numeric_values['space'])
        self.intensity.update(gestureInput.numeric_values['intensity'])
        
    def show(self, verbose = True):
        if verbose:
            print 'Area      = ',self.area.show() #,self.area.norm, '\t',self.area.min,' ',self.area.max,' ',self.area.raw
            print 'Time      = ',self.time.show()#self.time.norm, '\t',self.time.min,' ',self.time.max,' ',self.time.raw
            print 'Space     = ',self.space.show()#self.space.norm, '\t',self.space.min,' ',self.space.max,' ',self.space.raw
            print 'Intensity = ',self.intensity.show()#self.intensity.norm, '\t',self.intensity.min,' ',self.intensity.max,' ',self.intensity.raw
        else:
            print 'Area      = ',self.area.show()#self.area.norm
            print 'Time      = ',self.time.show()#self.time.norm
            print 'Space     = ',self.space.show()#self.space.norm
            print 'Intensity = ',self.intensity.show()#self.intensity.norm