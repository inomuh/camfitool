#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Real-time Fault Injection Python Class For Camera FI Demo Tool #


import cv2
from cv_bridge import CvBridge
from PIL import Image
import numpy as np
from imgaug import augmenters as iaa

class RealtimeImageFault(object):
    """
    TOF/RGB Camera Image (Realtime) Fault Library For Camera FI Demo Tool
    ----------------------------------------------------------------
    ### Variables:
        - image = Stream image
        - kernel = Image kernel info
        - fault_type: Choosing fault type
        - fault_rate: Fault rate (%) 


    ### TOF Image Faults (Under-development):
        - Salt&Pepper -> salt_pepper()
        - Gaussian -> gaussian()
        - Poisson -> poisson()

    ### RGB Image Faults:
        - Open -> open_fault()
        - Close -> close_fault()
        - Erosion -> erosion()
        - Dilation -> dilation()
        - Gradient -> gradient()
        - Motion-blur -> motion_blur()
        - Partialloss -> partialloss()

    ###### Created by AKE - 04.11.21
    """
    def __init__(self, image, kernel, fault_type, fault_rate):
        
        self.img = image
        self.kernel = kernel
        self.fault_type = fault_type
        self.fault_rate = fault_rate
        self.bridge = CvBridge()

    
    def open_fault(self):
        return cv2.morphologyEx(self.img, cv2.MORPH_OPEN, self.kernel)

    def close_fault(self):
        return cv2.morphologyEx(self.img, cv2.MORPH_CLOSE, self.kernel)
        
    def dilation(self):
        return cv2.dilate(self.img,self.kernel, iterations = 5)
    
    def erosion(self):
        return cv2.erode(self.img,self.kernel, iterations = 5) 

    def gradient(self):
        return cv2.morphologyEx(self.img, cv2.MORPH_GRADIENT, self.kernel)

    def partialloss(self):
        pass

    def motion_blur(self):
        return cv2.blur(self.img,(5,5))

    def saltpepper(self):
        pass
    
    def gaussian(self):
        pass

    def poisson(self):
        pass


