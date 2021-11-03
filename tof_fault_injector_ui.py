#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TOF Fault Injector For Camera FI Demo Tool #

import time
from os import listdir
from os.path import isfile, join
from class_tof_faults_offline_ui import TofImageFault as tfi
import os, sys
import random

def main(ndir_name, fdir_name, fault_type, fault_rate, randomized):
    """
    TOF Fault Injector UI modülü, Camera Fault Injector Demo Tool'dan gerekli değişkenleri alır, class_tof_faults_offline_ui class'ına uygun 
    bir şekilde gönderir. Tool'dan
    
    """
    img_format = ".bmp"
    img_name_list = read_image_list(ndir_name)
    fault_rate = int(fault_rate)/100
    randomValue = 0
    
    if fault_type == "Gaussian":
        fault_type = "g"
    elif fault_type == "Poisson":
        fault_type = "p"
    elif fault_type == "Salt&Pepper":
        fault_type = "s"
    else:
        pass

    fi_image_name_list = []
    
    if randomized == False:
        multi_fault_applier(img_name_list, ndir_name, fdir_name, img_format, fault_type, fault_rate)
        done = "Full Injection Completed!"
    else:
        length = len(img_name_list)
        randomValue = random.randrange(length)
        fi_image_name_list = random_fault_applier(img_name_list, ndir_name, fdir_name, img_format, fault_type, fault_rate, randomValue)
        done = "Randomized Injection Sequence Completed!\n----------------------------------\nFault Injected Image Value: "+str(randomValue)+"/"+str(len(img_name_list))
        fi_image_name_list.sort()
    
    return done, len(img_name_list), fi_image_name_list

def read_image_list(file_path):
    """
    TOF Resim klasöründeki resimlerin isimlerini bir listeye kaydeder.
    """
    onlyfiles = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    image_list = [i.split(".",1)[0] for i in onlyfiles]
    return image_list

def multi_fault_applier(img_name_list, ndir_name, fdir_name, img_format, fault_type, fault_rate):
    """
    Bir resim listesine çoklu hata uygulanmasını sağlar.
    """
    for i in range(len(img_name_list)):
        image_name= img_name_list[i]
        tf = tfi(ndir_name, fdir_name, image_name, img_format, fault_type, fault_rate)    
        tf.tof_image_fault()

def random_fault_applier(img_name_list,ndir_name, fdir_name, img_format, fault_type, fault_rate, randomValue):
    """
    Rastgele sayıda resim üzerinde hata enjeksiyonu yapmaya yarayan test fonksiyonudur.
    
    """
    fi_image_name_list = []

    for j in range(len(img_name_list)):
        image_name= img_name_list[j]
        tf = tfi(ndir_name, fdir_name, image_name, img_format, "nf", fault_rate)    
        tf.tof_image_fault()

    i = 0
    y = 0

    while i != randomValue: 
    #for i in range(randomValue):
        x = random.randint(1,4)
        image_name= img_name_list[y]
        
        if x%2 == 0:
            tf = tfi(ndir_name, fdir_name, image_name, img_format, fault_type, fault_rate)
            fi_image_name_list.append(image_name)
            tf.tof_image_fault()
            i+=1
        y+=1

        if y >= len(img_name_list):
            y = 0

    return fi_image_name_list

@classmethod
def get_current_workspace(cls):
    """
        Tool'un çalıştığı workspace konumunu veren fonksiyondur.
        
    """
    file_full_path = os.path.dirname(os.path.realpath(__file__))
    
    return file_full_path

if __name__ == "__main__":
    main()