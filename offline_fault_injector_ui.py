#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offline Fault Injector For Camera FI Demo Tool
"""

import os
from os import listdir
from os.path import isfile, join
import random
from class_fi_offline_ui import OfflineImageFault as ofi

# from class_list_creator import ListCreator as img_list


def main(
    ndir_name,
    fdir_name,
    fault_type,
    fault_rate,
    randomized,
    fimp_rate,
    last_fi_name_list,
):
    """
    Offline Camera Fault Injector UI module takes required variables from
    CamFITool and sends them to class_fi_offline_ui accordingly. This method,
    which is used to print an fault in the offline method (the method where
    a fault is printed in a ready image folder and saved in another folder),
    compiles the appropriate fault types determined for TOF and RGB image types.
    """

    img_format = str(img_format_finder(ndir_name))
    img_name_list = read_image_list(ndir_name)
    # Eger tekrarlı hata enj olursa hata uygulanmıs resimler, ana listeden
    # cikarilarak img_name_list olusturulur.
    if last_fi_name_list is not None:
        img_name_list = list_substractor(img_name_list, last_fi_name_list)

    fault_rate = int(fault_rate) / 100
    fimp_val = int(int(len(img_name_list)) * int(fimp_rate) / 100)
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
        if fimp_rate != 100:
            fi_image_name_list = random_fault_applier(
                img_name_list,
                ndir_name,
                fdir_name,
                img_format,
                fault_type,
                fault_rate,
                fimp_val,
            )
            done = (
                "Partial Injection Completed!\nFault Injected Image Value: "
                + str(fimp_val)
                + "/"
                + str(len(img_name_list))
            )
            fi_image_name_list.sort()
        else:
            multi_fault_applier(
                img_name_list, ndir_name, fdir_name, img_format, fault_type, fault_rate
            )
            done = "Full Injection Completed! Fault applied to all images."
    else:
        if fimp_rate != 100:
            print(
                "Randomized function cannot be applicable Fault Implementation Value type FI!"
            )
        length = len(img_name_list)
        random_value = random.randrange(length)
        fi_image_name_list = random_fault_applier(
            img_name_list,
            ndir_name,
            fdir_name,
            img_format,
            fault_type,
            fault_rate,
            random_value,
        )
        done = (
            "Randomized Injection Sequence Completed!\n"
            + "----------------------------------\nFault Injected Image Value: "
            + str(random_value)
            + "/"
            + str(len(img_name_list))
        )
        fi_image_name_list.sort()

    return done, len(img_name_list), fi_image_name_list


def list_substractor(norm_img_list, fi_img_list):
    """Liste ayırıcı"""
    return [x for x in norm_img_list if x not in fi_img_list]


def read_image_list(file_path):
    """
    TOF saves the names of the images in the Image folder in a list.
    """
    onlyfiles = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    image_list = [i.split(".", 1)[0] for i in onlyfiles]
    return image_list


def multi_fault_applier(
    img_name_list, ndir_name, fdir_name, img_format, fault_type, fault_rate
):
    """
    Allows multiple faults to be applied to a list of images.
    """
    for i, img in enumerate(img_name_list):
        image_name = [i, img]
        apply_fault = ofi(
            ndir_name, fdir_name, image_name[1], img_format, fault_type, fault_rate
        )

        apply_fault.main()


def random_fault_applier(
    img_name_list,
    ndir_name,
    fdir_name,
    img_format,
    fault_type,
    fault_rate,
    random_value,
):
    """
    It is a test function for injecting faults on a random number of images.
    """
    fi_image_name_list = []

    for i, img in enumerate(img_name_list):
        image_name = [i, img]
        apply_fault = ofi(
            ndir_name, fdir_name, image_name[1], img_format, "nf", fault_rate
        )

        if fault_type in {"s", "g", "p"}:
            apply_fault.tof_image_fault()
        else:
            apply_fault.rgb_image_fault()

    i_val = 0
    y_val = 0

    while i_val != random_value:
        x_val = random.randint(1, 4)
        image_name = img_name_list[y_val]

        if x_val % 2 == 0:
            apply_fault = ofi(
                ndir_name, fdir_name, image_name, img_format, fault_type, fault_rate
            )
            fi_image_name_list.append(image_name)

            if fault_type in {"s", "g", "p"}:
                apply_fault.tof_image_fault()
            else:
                apply_fault.rgb_image_fault()

            i_val += 1
        y_val += 1

        if y_val >= len(img_name_list):
            y_val = 0

    return fi_image_name_list


def img_format_finder(ndir_name):
    """
    This function reads the format of the images taken from the normal
    image database, and the faulty images are output in the same format.
    """
    one_image = os.listdir(ndir_name)[0]
    img_format = "." + one_image.split(".", 2)[1]

    return img_format
