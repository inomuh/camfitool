#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Fault Injection Python Class For Camera FI Demo Tool
"""

import cv2
from cv_bridge import CvBridge

class RealtimeImageFault:
    """
    TOF/RGB Camera Image (Realtime) Fault Library For Camera FI Demo Tool
    ----------------------------------------------------------------
    ### Variables:
        - image = Stream image
        - kernel = Image kernel info
        - fault_type: Choosing fault type
        - fault_rate: Fault rate (%)

    ### Image Faults :
        - Salt&Pepper -> salt_pepper() (Under-development)
        - Gaussian -> gaussian() (Under-development)
        - Poisson -> poisson() (Under-development)
        - Erosion -> erosion()
        - Dilation -> dilation()
        - Gradient -> gradient()
        - Partialloss -> partialloss() (Under-development)

    ###### Created by AKE - 23.08.22
    """
    def __init__(self, image, kernel, fault_type, fault_rate):
        self.img = image
        self.kernel = kernel
        self.fault_type = fault_type
        self.fault_rate = fault_rate
        self.bridge = CvBridge()

    def dilation(self):
        """Dilation Fault Method"""
        return cv2.dilate(self.img,self.kernel, iterations = 5)

    def erosion(self):
        """Erosion Fault Method"""
        return cv2.erode(self.img,self.kernel, iterations = 5)

    def gradient(self):
        """Gradient Fault Method"""
        return cv2.morphologyEx(self.img, cv2.MORPH_GRADIENT, self.kernel)

    def partialloss(self):
        """Partialloss Fault Method (Under-development)"""

    def saltpepper(self):
        """Salt&Pepper Fault Method (Under-development)"""

    def gaussian(self):
        """Gaussian Fault Method (Under-development)"""

    def poisson(self):
        """Poisson Fault Method (Under-development)"""
