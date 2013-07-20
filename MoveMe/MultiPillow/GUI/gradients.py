#Copyright 2006 DR0ID <dr0id@bluewin.ch> http://mypage.bluewin.ch/DR0ID
#
#
#
"""
Allow to draw some gradients relatively easy.
"""

__author__ = "$Author: DR0ID $"
__version__= "$Revision: 18 $"
__date__   = "$Date: 2006-10-03 14:01:03 +0200 (Di, 03 Okt 2006) $"

import pygame
import math


def gradient(surface, 
                startpoint, 
                endpoint, 
                startcolor, 
                endcolor,
                Rfunc = (lambda x:x), 
                Gfunc = (lambda x:x), 
                Bfunc = (lambda x:x), 
                Afunc = (lambda x:1), 
                type  = "line", 
                mode  = None ):
    '''
    surface   : surface to draw on
    startpoint: (x,y) point on surface
    endpoint  : (x,y) point on surface
    startcolor: (r,g,b,a) color at startpoint
    endcolor  : (r,g,b,a) color at endpoint
    Rfunc     : function y = f(x) with  startcolor =f(0) and endcolor = f(1) where 0 is at startpoint and 1 at endpoint
    Gfunc     :  ---  "  ---
    Bfunc     :  ---  "  ---
    Afunc     :  ---  "  ---
                these functions are evaluated in the range 0 <= x <= 1 and 0<= y=f(x) <= 1
    type      : "line", "circle" or "rect"
    mode      : "+", "-", "*", None (how the pixels are drawen)
    
    returns   : surface with the color characteristics w,h = (d, 256) and d = length of endpoint-startpoint
    
    '''
    dx = endpoint[0]-startpoint[0]
    dy = endpoint[1]-startpoint[1]
    d = int(round(math.hypot(dx, dy)))
    angle = math.degrees( math.atan2(dy, dx) )
    
    color = ColortInterpolator(d, startcolor, endcolor, Rfunc, Gfunc, Bfunc, Afunc)
    
    if type=="line":
        h = int(2.*math.hypot(*surface.get_size()))
        bigSurf = pygame.Surface((d, h)).convert_alpha()
        bigSurf.fill((0,0,0,0))
        bigSurf.set_colorkey((0,0,0, 0))
        
        for x in range(d):
            pygame.draw.line(bigSurf, color.eval(x), (x,0), (x,h), 1)
        bigSurf = pygame.transform.rotozoom(bigSurf, -angle, 1)
        bigSurf.set_colorkey((0,0,0, 0))
        rect = bigSurf.get_rect()
        srect = pygame.Rect(rect)
        dx = d/2. * math.cos(math.radians(angle))
        dy = d/2. * math.sin(math.radians(angle))
        rect.center = startpoint
        rect.move_ip(dx, dy)
        
    elif type=="circle":
        bigSurf = pygame.Surface((2*d, 2*d)).convert_alpha()
        bigSurf.fill((0,0,0,0))
        for x in range(d, 0, -1):
            pygame.draw.circle(bigSurf, color.eval(x), (d,d), x)
        rect = bigSurf.get_rect()
        srect = pygame.Rect(rect)
        rect.center = (startpoint[0], startpoint[1])
        
    elif type=="rect":
        bigSurf = pygame.Surface((2*d, 2*d)).convert_alpha()
        bigSurf.fill((0,0,0,0))
        c = bigSurf.get_rect().center
        for x in range(d,-1,-1):
            r = pygame.Rect(0,0,2*x,2*x)
            r.center = c
            pygame.draw.rect(bigSurf, color.eval(x), r)
        bigSurf = pygame.transform.rotozoom(bigSurf, -angle, 1)
        bigSurf.set_colorkey((0,0,0, 0))
        
        rect = bigSurf.get_rect()
        srect = pygame.Rect(rect)
        rect.center = startpoint
    else:
        raise NameError("type must be one of \"line\",\"circle\" or \"rect\"")
    
    if mode is None:
        surface.blit(bigSurf, rect, srect)
    else:
        if mode=="+":
            cf = pygame.color.add
        elif mode=="*":
            cf = pygame.color.multiply
        elif mode=="-":
            cf = pygame.color.subtract
        else:
            raise NameError("type must be one of \"+\", \"*\", \"-\" or None")
        irect = surface.get_clip().clip(rect)
        for x in range(irect.left, irect.left+irect.width):
            for y in range(irect.top, irect.top+irect.height):
                surface.set_at((x,y), cf(surface.get_at((x,y)), bigSurf.get_at((x-rect.left, y-rect.top)) ) )
    
    del bigSurf   
    char = pygame.Surface((d+1, 257))
    char.fill((0,0,0))
    ox = 0
    oldcol = color.eval(0)
    for x in range(d):
        col = color.eval(x)
        pygame.draw.line(char, (255,0,0), (x, 256-col[0]), (ox, 256-oldcol[0]))
        pygame.draw.line(char, (0,255,0), (x, 256-col[1]), (ox, 256-oldcol[1]))
        pygame.draw.line(char, (0,0,255), (x, 256-col[2]), (ox, 256-oldcol[2]))
        pygame.draw.line(char, (255,255,255), (x, 256-col[3]), (ox, 256-oldcol[3]))
        ox = x
        oldcol = col
     
    return char
        
    
    


class ColortInterpolator(object):
    '''
    ColorInterpolator(distance, color1, color2, rfunc, gfunc, bfunc, afunc)
    
    interpolates a color over the distance using different functions for r,g,b,a
    separately (a= alpha).
    '''
    def __init__(self, distance, color1, color2, rfunc, gfunc, bfunc, afunc):
        object.__init__(self)
        
        self.rInterpolator = FunctionInterpolator(color1[0], color2[0], distance, rfunc)
        self.gInterpolator = FunctionInterpolator(color1[1], color2[1], distance, gfunc)
        self.bInterpolator = FunctionInterpolator(color1[2], color2[2], distance, bfunc)
        if len(color1)==4 and len(color2)==4:
            self.aInterpolator = FunctionInterpolator(color1[3], color2[3], distance, afunc)
        else:
            self.aInterpolator = FunctionInterpolator(255, 255, distance, afunc)
            
    def eval(self, x):
        '''
        eval(x) -> color
        
        returns the color at the position 0<=x<=d (actually not bound to this interval).
        '''
##        print "colorInterp x", x, self.rInterpolator.eval(x), self.gInterpolator.eval(x), self.bInterpolator.eval(x)
        return [self.rInterpolator.eval(x), 
                self.gInterpolator.eval(x), 
                self.bInterpolator.eval(x), 
                self.aInterpolator.eval(x)]
            


class FunctionInterpolator(object):
    '''
    FunctionINterpolator(startvalue, endvalue, trange, func)
    
    interpolates a function y=f(x) in the range trange with
    startvalue = f(0)
    endvalue   = f(trange)
    using the function func
    '''
    def __init__(self, startvalue, endvalue, trange, func):
        object.__init__(self)
        # function
        self.func = func
        # y-scaling
        self.a = endvalue-startvalue
        if self.a == 0:
            self.a = 1.
        # x-scaling
        if trange!=0:
            self.b = 1./abs(trange)
        else:
            self.b = 1.
        # x-displacement
        self.c = 0
        # y-displacement
        self.d = min(max(startvalue,0),255)
        
    def eval(self, x):
        ''' 
        eval(x)->float
        
        return value at position x
        '''
        # make sure that the returned value is in [0,255]
        return int(round(min(max(self.a*self.func(self.b*(x+self.c))+self.d, 0), 255)))

    
    

#------------------------------------------------------------------------------


    

def genericFxyGradient(surf, clip, color1, color2, func, intx, yint, zint=None):
    """
    genericFxyGradient(size, color1, color2,func, intx, yint, zint=None)
    
    some sort of highfield drawer :-)
    
    surf   : surface to draw
    clip   : rect on surf to draw in
    color1 : start color
    color2 : end color
    func   : function z = func(x,y)
    xint   : interval in x direction where the function is evaluated
    yint   : interval in y direction where the function is evaluated
    zint   : if not none same as yint or xint, if None then the max and min value
             of func is taken as z-interval
    
    color = a*func(b*(x+c), d*(y+e))+f
    """
    # make shure that x1<x2 and y1<y2 and z1<z2
    w,h = clip.size
    x1 = min(intx)
    x2 = max(intx)
    y1 = min(yint)
    y2 = max(yint)
    if zint: # if user give us z intervall, then use it
        z1 = min(zint)
        z2 = max(zint)
    else: # look for extrema of function (not best algorithme)
        z1 = func(x1,y1)
        z2 = z1
        for i in range(w):
            for j in range(h):
                r = func(i,j)
                z1 = min(z1, r)
                z2 = max(z2, r)
                
    x1 = float(x1)
    x2 = float(x2)
    y1 = float(y1)
    y2 = float(y2)
    z1 = float(z1)
    z2 = float(z2)
    if len(color1)==3:
        color1 = list(color1)
        color1.append(255)
    if len(color2)==3:
        color2 = list(color2)
        color2.append(255)
    
    # calculate streching and displacement variables
    a = ((color2[0]-color1[0])/(z2-z1), \
         (color2[1]-color1[1])/(z2-z1), \
         (color2[2]-color1[2])/(z2-z1), \
         (color2[3]-color1[3])/(z2-z1) ) # streching in z direction
    b = (x2-x1)/float(w) # streching in x direction
    d = (y2-y1)/float(h) # streching in y direction
    f = ( color1[0]-a[0]*z1, \
          color1[1]-a[1]*z1, \
          color1[2]-a[2]*z1, \
          color1[3]-a[3]*z1 )# z displacement
    c = x1/b
    e = y1/d
    
    surff = pygame.surface.Surface((w,h)).convert_alpha()
    # generate values
    for i in range(h):
        for j in range(w):
            val = func(b*(j+c), d*(i+e))
            #clip color
            color = (   max(min(a[0]*val+f[0],255),0), \
                        max(min(a[1]*val+f[1],255),0), \
                        max(min(a[2]*val+f[2],255),0), \
                        max(min(a[3]*val+f[3],255),0) )
            surff.set_at( (j,i), color )
    surf.blit(surff, clip)



