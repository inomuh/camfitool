#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOF Fault Injector For Camera FI Demo Tool
ROS Edition
"""
import os
from os import listdir
from os.path import isfile, join
import random
from class_fi_offline_ui import OfflineImageFault as ofi

def main(ndir_name, fdir_name, camera_type, fault_type, fault_rate, randomized):
    """
    Offline Camera Fault Injector UI modülü, Camera Fault Injector Demo Tool'dan
    gerekli değişkenleri alır, class_fi_offline_ui class'ına uygun bir şekilde gönderir.
    Offline yönteminde (hazır bir resim klasörüne hata basılıp, bir başka klasöre kayıt
    yapılan yöntem) hata basmaya yarayan bu yöntem TOF ve RGB resim türleri için belirlenmiş
    uygun hata tiplerini derler.
    """
    # Şu an elimizdeki kütüphane .bmp uzantılı, ancak rgb resimler söz konusu
    # olursa img_format değişkeni bu doğrultuda düzenlenecek.

    img_format= str(img_format_finder(ndir_name))
    img_name_list = read_image_list(ndir_name)
    fault_rate = int(fault_rate)/100
    random_value = 0

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

    if randomized is False:
        multi_fault_applier(img_name_list, ndir_name, fdir_name, img_format,\
             camera_type, fault_type, fault_rate)
        done = "Full Injection Completed!"
    else:
        length = len(img_name_list)
        random_value = random.randrange(length)
        fi_image_name_list = random_fault_applier(img_name_list, ndir_name,\
             fdir_name, img_format, camera_type, fault_type, fault_rate, random_value)
        done = "Randomized Injection Sequence Completed!\n"+\
            "----------------------------------\nFault Injected Image Value: "+\
                str(random_value)+"/"+str(len(img_name_list))
        fi_image_name_list.sort()

    return done, len(img_name_list), fi_image_name_list

def read_image_list(file_path):
    """
    TOF Resim klasöründeki resimlerin isimlerini bir listeye kaydeder.
    """
    onlyfiles = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    image_list = [i.split(".",1)[0] for i in onlyfiles]
    return image_list

def multi_fault_applier(img_name_list, ndir_name, fdir_name, img_format, camera_type,\
     fault_type, fault_rate):
    """
    Bir resim listesine çoklu hata uygulanmasını sağlar.
    """
    for i, img in enumerate(img_name_list):
        image_name = [i,img]
        apply_fault = ofi(ndir_name, fdir_name, image_name[1], img_format, camera_type,\
             fault_type, fault_rate)

        apply_fault.main()

def random_fault_applier(img_name_list,ndir_name, fdir_name, img_format, camera_type,\
     fault_type, fault_rate, random_value):
    """
    Rastgele sayıda resim üzerinde hata enjeksiyonu yapmaya yarayan test fonksiyonudur.
    """
    fi_image_name_list = []

    for i, img in enumerate(img_name_list):
        image_name = [i, img]
        apply_fault = ofi(ndir_name, fdir_name, image_name[1], img_format, camera_type,\
             "nf", fault_rate)

        if fault_type in {"s", "g", "p"}:
            apply_fault.tof_image_fault()
        else:
            apply_fault.rgb_image_fault()

    i_val = 0
    y_val = 0

    while i_val != random_value:
        x_val = random.randint(1,4)
        image_name= img_name_list[y_val]

        if x_val%2 == 0:
            apply_fault = ofi(ndir_name, fdir_name, image_name, img_format, camera_type,\
                 fault_type, fault_rate)
            fi_image_name_list.append(image_name)

            if fault_type in {"s", "g", "p"}:
                apply_fault.tof_image_fault()
            else:
                apply_fault.rgb_image_fault()

            i_val+=1
        y_val+=1

        if y_val >= len(img_name_list):
            y_val = 0

    return fi_image_name_list

def img_format_finder(ndir_name):
    """
    Bu fonksiyon, normal resim veritabanından alınan resimlerin hangi
    formatta olduklarını okur, hatalı resimler de aynı formatta
    çıkarılır.
    """
    one_image = os.listdir(ndir_name)[0]
    img_format = "." + one_image.split(".",2)[1]

    return img_format
