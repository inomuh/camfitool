"""
Bu script, camfitool_main ve fi_anomaly_detector_main üzerinde tutulmaya gerek olmayan ekstra fonksiyonların
tutulduğu scripttir. Main üzerinden çağrılarak fonksiyonlar kullanılır.
"""

import os
from os import listdir
from os.path import isfile, join
import datetime
from gui_restart_app import restart_program as rest

def reset_button_function():
    """When the reset button clicked, all interface will be reset"""
    rest()

def go_fiad_app_func():
    """When the GO FIAD button clicked, open the fiad app"""
    os.system("python3 fi_anomaly_detector_main.py")


def list_substractor(norm_img_list, fi_img_list):
    """Liste ayırıcı"""
    return [x for x in norm_img_list if x not in fi_img_list]

def read_image_list(file_path):
    """
    Image list reader
    """
    onlyfiles = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    image_list = [i.split(".", 1)[0] for i in onlyfiles]
    return image_list

def get_current_workspace():
    """
    It is the function that gives the workspace location where the Tool works.
    """
    file_full_path = os.path.dirname(os.path.realpath(__file__))
    return file_full_path

def error_log_creator(msg_data):
    """
    It is the function that allows to keep a record of the error details
    when the interface gives an error message.
    """
    curr_workspace = get_current_workspace()
    try:
        os.makedirs("logs")
    except OSError:
        pass

    curr_date = datetime.datetime.now()
    with open(
        str(curr_workspace)
        + "/logs/error_log_"
        + str(curr_date.hour)
        + str(curr_date.minute)
        + str(curr_date.second)
        + ".txt",
        "w",
        encoding="utf-8",
    ) as error_log:
        error_log.write(f"ERROR: {curr_date.ctime()}:\n---\n {msg_data}\n")

def get_class_names(train_dir):
    """
    Sınıf isimlerini yükler.
    """
    # Let's get the class names
    import pathlib
    import numpy as np

    data_dir = pathlib.Path(train_dir)
    class_names = np.array(sorted([item.name for item in data_dir.glob("*")]))
    return class_names

def str_splitter(str_to_split):
    """
    Stringi split eder.
    """
    return str_to_split.split("/")[-1]