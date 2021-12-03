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
        """Open Fault Method"""
        return cv2.morphologyEx(self.img, cv2.MORPH_OPEN, self.kernel)

    def close_fault(self):
        """Close Fault Method"""
        return cv2.morphologyEx(self.img, cv2.MORPH_CLOSE, self.kernel)

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

    def motion_blur(self):
        """Motion-blur Fault Method"""
        return cv2.blur(self.img,(5,5))

    def saltpepper(self):
        """Salt&Pepper Fault Method (Under-development)"""

    def gaussian(self):
        """Gaussian Fault Method (Under-development)"""

    def poisson(self):
        """Poisson Fault Method (Under-development)"""
