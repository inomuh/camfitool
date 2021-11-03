#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import os
import sys

from cv_bridge import CvBridge
import numpy as np
from PIL import Image
import numpy as np
from imgaug import augmenters as iaa


class TofImageFault(object):
    """
    TOF Camera Image (Offline) Fault Library For Camera FI Demo Tool
    ----------------------------------------------------------------
    ### Variables:
        - ndir_name: Normal image directory (input file) name
        - fdir_name: Faulty image directory (output file) name
        - img_name: Image name
        - img_format: Image format (.bmp, .png etc.)
        - fault_type: Choosing fault type
        - fault_rate: Fault rate (%) 
        
    ### TOF Image Faults:
        - Salt&Pepper -> salt_pepper()
        - Gaussian -> gaussian()
        - Poisson -> poisson()

    ###### Created by AKE - 26.10.21
    """
    def __init__(self, ndir_name, fdir_name, img_name, img_format, fault_type, fault_rate):

        self.ndir_name = ndir_name
        self.fdir_name = fdir_name
        self.img_name = img_name
        self.img_format = img_format
        self.fault_type = fault_type
        self.fault_rate = fault_rate
        self.bridge = CvBridge()


    def tof_image_fault(self):   
        """
        TOF Image Faults:
        - Salt&Pepper -> salt_pepper()
        - Gaussian -> gaussian()
        - Poisson -> poisson()
    
        """ 
        try:
            im = Image.open(self.ndir_name + self.img_name + self.img_format)
            im_arr = np.asarray(im)
            
            if self.fault_type != "nf":
                if self.fault_type == "s":
                    aug = self.salt_pepper(self.fault_rate)
                elif self.fault_type == "g":
                    aug = self.gaussian(self.fault_rate)
                elif self.fault_type == "p":
                    aug = self.poisson(self.fault_rate)
                else:
                    print("This fault cannot be found. Try again...")
                    exit()

                im_arr = aug.augment_image(im_arr)

            im = Image.fromarray(im_arr).convert('L')
            im = np.array(im)
            image_name = str(self.img_name + self.img_format)
            cv2.imwrite(os.path.join(self.fdir_name, image_name), im) # saving faulty tof image
            

        except Exception as err:
            print(err)

    def salt_pepper(self, fr):
        # salt and pepper noise
        aug = iaa.SaltAndPepper(p = fr)
        return aug
            
    def gaussian(self, fr):
        # gausian noise
        aug = iaa.AdditiveGaussianNoise(loc=0, scale=fr*255)
        return aug

    def poisson(self, fr):
        # poisson noise
        fr = float(fr*100)
        aug = iaa.AdditivePoissonNoise(lam=fr, per_channel=True)
        return aug
