#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TOF Fault Injector For Camera FI Demo Tool #

from os import listdir
from os.path import isfile, join
from class_fi_offline_ui import OfflineImageFault as ofi
import os
import random

def main(ndir_name, fdir_name, camera_type, fault_type, fault_rate, randomized):
    """
    Offline Camera Fault Injector UI modülü, Camera Fault Injector Demo Tool'dan gerekli değişkenleri alır, class_fi_offline_ui class'ına uygun 
    bir şekilde gönderir. Offline yönteminde (hazır bir resim klasörüne hata basılıp, bir başka klasöre kayıt yapılan yöntem) hata basmaya yarayan bu yöntem
    TOF ve RGB resim türleri için belirlenmiş uygun hata tiplerini derler.
    
    """

    img_format = ".bmp" # Şu an elimizdeki kütüphane .bmp uzantılı, ancak rgb resimler söz konusu olursa img_format değişkeni bu doğrultuda düzenlenecek.
    img_name_list = read_image_list(ndir_name)
    fault_rate = int(fault_rate)/100
    randomValue = 0

    ## TOF Fault Types##
    if fault_type == "Gaussian":
        fault_type = "g"
    elif fault_type == "Poisson":
        fault_type = "p"
    elif fault_type == "Salt&Pepper":
        fault_type = "s"
        
    ## RGB Fault Types ##
    elif fault_type == "Open":
        fault_type = "o"
    elif fault_type == "Close":
        fault_type = "c"
    elif fault_type == "Dilation":
        fault_type = "d"
    elif fault_type == "Erosion":
        fault_type = "e"
    elif fault_type == "Gradient":
        fault_type = "gr"
    elif fault_type == "Motion-blur":
        fault_type = "m"
    elif fault_type == "Partialloss":
        fault_type = "par"
    else:
        pass    
    
    fi_image_name_list = []
    
    if randomized == False:
        multi_fault_applier(img_name_list, ndir_name, fdir_name, img_format, camera_type, fault_type, fault_rate)
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

def multi_fault_applier(img_name_list, ndir_name, fdir_name, img_format, camera_type, fault_type, fault_rate):
    """
    Bir resim listesine çoklu hata uygulanmasını sağlar.
    """
    for i in range(len(img_name_list)):
        image_name= img_name_list[i]
        tf = ofi(ndir_name, fdir_name, image_name, img_format, camera_type, fault_type, fault_rate)

        tf.main()

def random_fault_applier(img_name_list,ndir_name, fdir_name, img_format, fault_type, fault_rate, randomValue):
    """
    Rastgele sayıda resim üzerinde hata enjeksiyonu yapmaya yarayan test fonksiyonudur.
    
    """
    fi_image_name_list = []

    for j in range(len(img_name_list)):
        image_name= img_name_list[j]
        tf = ofi(ndir_name, fdir_name, image_name, img_format, "nf", fault_rate)    
        
        if fault_type == "s" or "g" or "p":    
            tf.tof_image_fault()
        else:
            tf.rgb_image_fault()

    i = 0
    y = 0

    while i != randomValue: 
    #for i in range(randomValue):
        x = random.randint(1,4)
        image_name= img_name_list[y]
        
        if x%2 == 0:
            tf = ofi(ndir_name, fdir_name, image_name, img_format, fault_type, fault_rate)
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