#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Offline Fault Injection Python Class For Camera FI Demo Tool #

import cv2
import os
from cv_bridge import CvBridge
import numpy as np
from PIL import Image
import numpy as np
from imgaug import augmenters as iaa


class OfflineImageFault(object):
    """
    TOF/RGB Camera Image (Realtime) Fault Library For Camera FI Demo Tool
    ----------------------------------------------------------------
    ### Variables:
        - ndir_name: Normal image directory (input file) name
        - fdir_name: Faulty image directory (output file) name
        - img_name: Image name
        - img_format: Image format (.bmp, .png etc.)
        - camera_type: TOF or RGB
        - fault_type: Choosing fault type
        - fault_rate: Fault rate (%) 
        
    ### TOF Image Faults:
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
    def __init__(self, ndir_name, fdir_name, img_name, img_format, camera_type, fault_type, fault_rate):

        self.ndir_name = ndir_name
        self.fdir_name = fdir_name
        self.img_name = img_name
        self.img_format = img_format
        self.fault_type = fault_type
        self.camera_type = camera_type
        self.fault_rate = fault_rate
        self.bridge = CvBridge()


    def main(self):

        if self.camera_type == "TOF":
            self.tof_image_fault()
        elif self.camera_type == "RGB":
            self.rgb_image_fault()
        else:
            print("Error")

    def tof_image_fault(self):   
        """
        TOF Image Faults:
        - Salt&Pepper -> salt_pepper()
        - Gaussian -> gaussian()
        - Poisson -> poisson()
    
        """ 
        #print(self.ndir_name, self.fdir_name, self.img_name, self.img_format, self.fault_type, self.fault_rate)        

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

    def rgb_image_fault(self):
        """
        RGB Image Faults:
            - Open -> open_fault()
            - Close -> close_fault()
            - Erosion -> erosion()
            - Dilation -> dilation()
            - Gradient -> gradient()
            - Motion-blur -> motion_blur()
            - Partialloss -> partialloss()
        
        """
        fr = int(self.fault_rate * 20) # Normalde fault rate yüzdelik olarak geldiğinden (TOF için düzenlenmişti), o değerin 0-20 aralığına getirilmesi sağlandı.  
        kernel = np.ones((fr,fr),np.uint8)
        try:
            im = cv2.imread(self.ndir_name + self.img_name + self.img_format)
            if self.fault_type != "nf":
                if self.fault_type == "o":
                    im = self.open_fault(im, kernel)
                elif self.fault_type == "c":
                    im = self.close_fault(im, kernel)
                elif self.fault_type == "e":
                    im = self.erosion(im, kernel)
                elif self.fault_type == "d":
                    im = self.dilation(im, kernel)
                elif self.fault_type == "gr":
                    im = self.gradient(im, kernel)
                elif self.fault_type == "m":
                    im = self.motion_blur(im, fr)
                elif self.fault_type == "par":
                    im = self.partialloss(im, kernel)        
                else:
                    print("This fault cannot be found. Try again...")
                    exit()

            img_format = ".png" # RGB tipinde kaydetmek için. Değiştirilebilir.
            image_name = str(self.img_name + img_format)
            cv2.imwrite(os.path.join(self.fdir_name, image_name), im) # saving faulty tof image
            

        except Exception as err:
            print(err)


    ### TOF Faults ###
    def salt_pepper(self, fr):
        # salt and pepper noise
        aug = iaa.SaltAndPepper(p = fr)
        return aug
            
    def gaussian(self, fr):
        # gausian noise
        aug = iaa.AdditiveGaussianNoise(loc=0, scale=fr*255)
        return aug

    def laplacian(self, fr): # Will Be Added.
        # laplacian noise
        aug = iaa.AdditiveLaplaceNoise(loc=0, scale=fr*255)
        return aug

    def poisson(self, fr):
        # poisson noise
        fr = float(fr*100)
        aug = iaa.AdditivePoissonNoise(lam=fr, per_channel=True)
        return aug

    ### RGB Faults ###
    def open_fault(self, img, k):
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, k)

    def close_fault(self, img, k):
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, k)
        
    def dilation(self, img, k):
        return cv2.dilate(img,k, iterations = 5)
    
    def erosion(self, img, k):
        return cv2.erode(img,k, iterations = 5) 

    def gradient(self, img, k):
        return cv2.morphologyEx(img, cv2.MORPH_GRADIENT, k)

    def partialloss(self, img):
        ###Eklenecek.
        pass

    def motion_blur(self, img, fr):
        return cv2.blur(img,(fr, fr))