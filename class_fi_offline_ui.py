#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offline Fault Injection Python Class For Camera FI Demo Tool
"""

import os
import sys
import cv2
from cv_bridge import CvBridge
import numpy as np
from PIL import Image
from imgaug import augmenters as iaa


class OfflineImageFault:
    """
    ### Variables:
        - ndir_name: Normal image directory (input file) name
        - fdir_name: Faulty image directory (output file) name
        - img_name: Image name
        - img_format: Image format (.bmp, .png etc.)
        - fault_type: Choosing fault type
        - fault_rate: Fault rate (%)

    ### Image Faults:
        - Salt&Pepper -> salt_pepper()
        - Gaussian -> gaussian()
        - Poisson -> poisson()
        - Erosion -> erosion()
        - Dilation -> dilation()
        - Gradient -> gradient()
        - Partialloss -> partialloss() (Under-dev)
        - Laplacian -> laplacian() (Under-dev)

    ###### Created by AKE - 23.08.22
    """

    def __init__(
        self, ndir_name, fdir_name, img_name, img_format, fault_type, fault_rate
    ):

        self.ndir_name = ndir_name
        self.fdir_name = fdir_name
        self.img_name = img_name
        self.img_format = img_format
        self.fault_type = fault_type
        self.fault_rate = fault_rate
        self.bridge = CvBridge()

    def main(self):
        """Main Function"""
        if self.fault_type == "s" or self.fault_type == "g" or self.fault_type == "p":
            self.tof_image_fault()
        elif (
            self.fault_type == "o"
            or self.fault_type == "c"
            or self.fault_type == "e"
            or self.fault_type == "d"
            or self.fault_type == "gr"
            or self.fault_type == "m"
            or self.fault_type == "par"
        ):
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
        try:
            image_file = Image.open(self.ndir_name + self.img_name + self.img_format)
            im_arr = np.asarray(image_file)

            if self.fault_type != "nf":
                if self.fault_type == "s":
                    aug_img = self.salt_pepper(self.fault_rate)
                elif self.fault_type == "g":
                    aug_img = self.gaussian(self.fault_rate)
                elif self.fault_type == "p":
                    aug_img = self.poisson(self.fault_rate)
                else:
                    print("This fault cannot be found. Try again...")
                    sys.exit()

                im_arr = aug_img.augment_image(im_arr)
            image_file = Image.fromarray(im_arr).convert("L")
            image_file = np.array(image_file)
            image_name = str(self.img_name + self.img_format)
            # saving faulty tof image
            cv2.imwrite(os.path.join(self.fdir_name, image_name), image_file)

        except Exception as error_msg:
            print(error_msg)

    def rgb_image_fault(self):
        """
        RGB Image Faults:
            - Erosion -> erosion()
            - Dilation -> dilation()
            - Gradient -> gradient()
            - Partialloss -> partialloss()
        """
        # Normally, since the fault rate comes as a percentage (it was arranged for TOF),
        # it is provided to bring that value to the range of 0-20.
        fi_rate = int(self.fault_rate * 20)
        kernel = np.ones((fi_rate, fi_rate), np.uint8)
        try:
            image_file = cv2.imread(self.ndir_name + self.img_name + self.img_format)

            if self.fault_type != "nf":
                if self.fault_type == "e":
                    image_file = self.erosion(image_file, kernel)
                elif self.fault_type == "d":
                    image_file = self.dilation(image_file, kernel)
                elif self.fault_type == "gr":
                    image_file = self.gradient(image_file, kernel)
                elif self.fault_type == "par":
                    image_file = self.partialloss(image_file, kernel)
                else:
                    print("This fault cannot be found. Try again...")
                    sys.exit()

            image_name = str(self.img_name + self.img_format)
            # saving faulty tof image
            cv2.imwrite(os.path.join(self.fdir_name, image_name), image_file)

        except Exception as error_msg:
            print(error_msg)

    ### TOF Faults ###
    @classmethod
    def salt_pepper(cls, fi_rate):
        """Salt&Pepper Noise"""
        aug_img = iaa.SaltAndPepper(p=fi_rate)
        return aug_img

    @classmethod
    def gaussian(cls, fi_rate):
        """Gaussian Noise"""
        aug_img = iaa.AdditiveGaussianNoise(scale=fi_rate * 255, per_channel=True)
        return aug_img

    @classmethod
    def laplacian(cls, fi_rate):  # Will Be Added.
        """Laplacian Noise (Under-development)"""
        aug_img = iaa.AdditiveLaplaceNoise(loc=0, scale=fi_rate * 255)
        return aug_img

    @classmethod
    def poisson(cls, fi_rate):
        """Poisson Noise"""
        fi_rate = float(fi_rate * 100)
        aug_img = iaa.AdditivePoissonNoise(lam=fi_rate, per_channel=True)
        return aug_img

    ### RGB Faults ###
    @classmethod
    def dilation(cls, img_msg, k):
        """Dilation FI Method"""
        return cv2.dilate(img_msg, k, iterations=5)

    @classmethod
    def erosion(cls, img_msg, k):
        """Erosion FI Method"""
        return cv2.erode(img_msg, k, iterations=5)

    @classmethod
    def gradient(cls, img_msg, k):
        """Gradient FI Method"""
        return cv2.morphologyEx(img_msg, cv2.MORPH_GRADIENT, k)

    @classmethod
    def partialloss(cls, img_msg, kernel):
        """Partialloss FI Method (Under-development)"""
