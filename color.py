'''
@author: vivek
'''
import math

class Color(object):
    '''
    classdocs
    '''


    def __init__(self, rgb):
        '''
        Precompute and keep the normalized values for r, g and b calculated from the raw rgb values given in the argument rgb.
        Raw rgb - (R, G, B) where all three are integers in the range 0-255
        Also have the total raw RGB in case you want to recover the raw rgb values
        The other attribute (apart from total, and normalized rgb values) you would need is intensity - total/3
        '''
       
        
        if (rgb[0] == 0 and rgb[1] == 0 and rgb[2] == 0):
            self.norm_r = self.norm_g = self.norm_b = 0
        
        else:
            self.norm_r = float (rgb[0]) / ((rgb[0] + rgb[1] + rgb[2]))
            self.norm_g = float (rgb[1]) / ((rgb[0] + rgb[1] + rgb[2]))
            self.norm_b = float (rgb[2]) / ((rgb[0] + rgb[1] + rgb[2]))
        
        self.total = float (rgb[0] + rgb[1] + rgb[2])
        self.intensity = self.total/3
        
        self.red = self.norm_r * self.total
        self.green = self.norm_g * self.total
        self.blue = self.norm_b * self.total


    def hue(self):
        '''
        Return the hue in radians - calculated as atan((sqrt(3)*(green-blue))/((red-green) + (red-blue)))
        The color values in the formula are the normalized color values
        You need to check if the denominator is zero and if it is return the appropriate value for the atan.
        '''
       
        
        if (self.norm_r - self.norm_g) + (self.norm_r - self.norm_b) == 0:
            return math.pi / 2
        
        return math.atan((math.sqrt(3)*(self.norm_g - self.norm_b))/
                         ((self.norm_r - self.norm_g) +
                          (self.norm_r - self.norm_b)))


    def hue_degrees(self):
        '''
        Return the hue in degrees
        '''
       
        
        return math.degrees(self.hue())


    def rgb_abs(self):
        '''
        Recover and return the raw RGB values as a triple of integers
        '''
       
        
        return ((self.norm_r * self.total,
                 self.norm_g * self.total,
                 self.norm_b * self.total))

    
