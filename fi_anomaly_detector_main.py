"""
FI Anomaly Detector (FIAD) Addition
-----------------------------------------------
This tool is a simple interface that allows detecting anomalies of fault
injected images.
"""
__author__ = "Alim Kerem Erdogmus"
__version__ = "v2.2.0"
__email__ = "kerem.erdogmus@inovasyonmuhendislik.com"
__status__ = "Beta"

import datetime
import time
import shutil
import os
import sys
import cv2
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QPushButton,
    QLabel,
    QFileDialog,
    QTextBrowser,
    QProgressBar,
    QMessageBox,
    QAction,
    QMenu,
)
from PyQt5 import uic
from PyQt5.QtGui import QPixmap

from PyQt5.QtCore import *

from fi_detector_main_ui_v2_1 import Ui_MainWindow
import extras as ext

import fnmatch
from PyQt5 import QtTest


class FIAnomalyDetector(QMainWindow):
    """
    FIAnomalyDetector Interface MainWindow Class
    """

    def __init__(self):
        # super(FIAnomalyDetector, self).__init__()

        # Load the ui file
        # uic.loadUi("fi_detector_interface_v2_0.ui", self)

        ## Alternative way to load the ui file
        QMainWindow.__init__(self)
        self.ui_main = Ui_MainWindow()
        self.ui_main.setupUi(self)
        self.show()

        # Define our widgets
        self.pred_button = self.findChild(QPushButton, "start_prediction_button")
        self.find_multi_model_button = self.findChild(
            QPushButton, "find_multi_model_file_button"
        )
        self.find_binary_model_button = self.findChild(
            QPushButton, "find_binary_model_file_button"
        )
        self.find_test_image_button = self.findChild(
            QPushButton, "find_test_image_button"
        )
        self.random_image_select_button = self.findChild(
            QPushButton, "random_image_select_button"
        )
        self.full_scan_button = self.findChild(QPushButton, "full_scan_button")
        self.save_pred_button = self.findChild(QPushButton, "save_pred_results_button")
        self.image_screen = self.findChild(QLabel, "prediction_image_show")
        self.multi_model_folder_textbox = self.findChild(
            QTextBrowser, "multi_model_location_text"
        )
        self.binary_model_folder_textbox = self.findChild(
            QTextBrowser, "binary_model_location_text"
        )
        self.info_screen = self.findChild(QLabel, "infoText")
        self.pred_result_text_screen = self.findChild(
            QLabel, "prediction_result_text_screen"
        )

        ### MENUBAR ###
        # FILE MENU
        self.new_menu = self.findChild(QAction, "actionNew")
        self.save_menu = self.findChild(QAction, "actionSave_Results")
        self.quit_menu = self.findChild(QAction, "actionQuit")
        # ABOUT MENU
        self.about_valu3s = self.findChild(QAction, "actionVALU3S")
        self.about_imtgd = self.findChild(QAction, "actionIMTGD")
        self.about_camfitool = self.findChild(QAction, "actionCamFITool")
        # HELP MENU
        self.help_menu = self.findChild(QAction, "actionUsageInfo")
        ### END MENUBAR ###

        # Click the Buttons
        self.find_multi_model_button.clicked.connect(
            self.find_multi_model_folder
        )  # Find Multi Model Button
        self.find_binary_model_button.clicked.connect(
            self.find_binary_model_folder
        )  # Binary model button
        self.find_test_image_button.clicked.connect(self.find_test_image)
        self.random_image_select_button.clicked.connect(self.random_image_select)
        self.full_scan_button.clicked.connect(self.full_scan_test)

        self.pred_button.clicked.connect(self.start_prediction)
        self.save_pred_button.clicked.connect(self.prediction_result_saver)

        self.new_menu.triggered.connect(ext.reset_button_function)
        self.save_menu.triggered.connect(self.prediction_result_saver)
        self.quit_menu.triggered.connect(sys.exit)
        self.help_menu.triggered.connect(self.usage_info)
        # Will be added
        self.about_camfitool.triggered.connect(ext.camfitool_web)
        self.about_valu3s.triggered.connect(ext.valu3s_web)
        self.about_imtgd.triggered.connect(ext.imtgd_web)

        self.info_screen.setText("> Welcome to the FI Anomaly Detector.")

        self.prediction_label = self.findChild(QLabel, "prediction_result_text_label")
        # self.prediction_label.setEnabled(False)

        # Version info
        self.version_info = self.findChild(QLabel, "version_info_label")
        self.version_info.setText("Version 2.2")

        # Show the app
        self.show()

    def prediction_result_saver(self):
        """
        Prediction işlemleri sonrası tüm sonuçları bir dosyaya kaydetmek
        için kullanılır.(The registration system made in this section will be arranged with
        a .json extension later.)
        """
        BINARY_MODEL_NAME = self.ui_main.binary_model_location_text.toPlainText()
        MULTICLASS_MODEL_NAME = self.ui_main.multi_model_location_text.toPlainText()
        TEST_IMAGE_NAME = self.ui_main.test_image_text.toPlainText()
        PREDICTION_RESULT = self.ui_main.prediction_result_text_screen.text()

        try:
            # S_File will get the directory path and extension.
            save_file = QFileDialog.getSaveFileName(
                None,
                "Save Config",
                str(ext.get_current_workspace()) + "/saves/saved_config",
                "Text Files (*.txt)",
            )

            save_text = f"Binary Model Name: {BINARY_MODEL_NAME}\nMulticlass Model Name: {MULTICLASS_MODEL_NAME}\nTest Image Name: {TEST_IMAGE_NAME}\nPrediction Result: {PREDICTION_RESULT}"

            # This will prevent you from an error if pressed cancel on file dialog.
            if save_file[0]:
                # Finally this will Save your file to the path selected.
                with open(save_file[0], "w", encoding="utf-8") as temp_file:
                    date = datetime.datetime.now()
                    temp_file.write("Created: " + str(date.ctime()))
                    temp_file.write("\n----------------------------------\n")
                    temp_file.write(save_text)

            self.info_screen.setText("Prediction configs saved!")

        except Exception as e:
            self.pop_up_message(e)

    def image_shape_fixer(self, filename, image_shape):
        """
        Reads an image from filename, turns it into a tensor and reshapes it
        to (img_shape, img_shape, colour_channels).
        """
        # Prediction for .bmp image (specialized)
        TEMP_IMAGE_NAME = ".temp_image.bmp"
        img = tf.keras.preprocessing.image.load_img(
            filename, target_size=(image_shape, image_shape)
        )
        img = tf.keras.preprocessing.image.img_to_array(img)
        status = cv2.imwrite(TEMP_IMAGE_NAME, img)
        img = img / 255.0
        return img, TEMP_IMAGE_NAME

    def show_image_file(self, fname):
        """
        Deneme fonksiyonu. Butona basıldığında dosya konumunda
        seçilen bir resmi ekrana basar. Düzenlenecek.
        """
        img, img_name = self.image_shape_fixer(
            fname[0], 256
        )  # Resmi 256x256 olarak ayarla
        # Open the image
        self.pixmap = QPixmap(img_name)
        # Add label to pic
        self.image_screen.setPixmap(self.pixmap)

    def find_multi_model_folder(self):
        """
        Select Model butonuna basıldığında kullanıcıdan model
        dosyalarının olduğu klasörü seçtirir.
        """
        model_fname = QFileDialog.getExistingDirectory(
            self,
            "Select Model Folder",
            "/home/ros/Desktop/VALU3S/CamFITool_arsiv/CamFITool_v1.4" + "/models",
        )
        if model_fname:
            model_fname = ext.str_splitter(model_fname)
            self.multi_model_folder_textbox.setText(model_fname)
            print(model_fname)
        else:
            self.pop_up_message("Model folder not selected!")

    def find_binary_model_folder(self):
        """
        Select Model butonuna basıldığında kullanıcıdan model
        dosyalarının olduğu klasörü seçtirir.
        """
        model_fname = QFileDialog.getExistingDirectory(
            self,
            "Select Model Folder",
            "/home/ros/Desktop/VALU3S/CamFITool_arsiv/CamFITool_v1.4" + "/models",
        )
        if model_fname:
            model_fname = ext.str_splitter(model_fname)
            self.binary_model_folder_textbox.setText(model_fname)
            print(model_fname)
        else:
            self.pop_up_message("Model folder not selected!")

    def find_test_image(self):
        """
        Select Test Image butonuna basıldığında kullanıcıdan test
        image seçimi istenir.
        """
        try:
            if (
                self.multi_model_folder_textbox.toPlainText() != ""
                and self.binary_model_folder_textbox.toPlainText() == ""
            ):
                test_image_fname = QFileDialog.getOpenFileName(
                    self,
                    "Select Test Image",
                    "/home/ros/Desktop/Tools/CAMFITOOL_v1.5/single_prediction",
                )
                self.show_image_file(test_image_fname)
                test_image_fname = ext.str_splitter(test_image_fname[0])
                self.ui_main.test_image_text.setText(test_image_fname)
            else:
                test_image_fname = QFileDialog.getOpenFileName(
                    self,
                    "Select Test Image",
                    "/home/ros/Desktop/Tools/CAMFITOOL_v1.5/single_prediction",
                )
                self.show_image_file(test_image_fname)
                test_image_fname = ext.str_splitter(test_image_fname[0])
                self.ui_main.test_image_text.setText(test_image_fname)

        except Exception:
            self.pop_up_message("Please select a valid image!")

    def random_image_select(self):
        """
        Random image select butonuna basıldığında kullanıcıdan
        random image seçimi istenir.
        """
        import random

        try:
            random_image_fname_list = []
            random_image_fname = ext.get_current_workspace() + "/single_prediction"
            # print(random_image_fname)
            # Get a random image path
            random_image = random.sample(os.listdir(random_image_fname), 1)
            print(random_image)
            random_image_fname_list.append(random_image_fname + "/" + random_image[0])
            # print(random_image_fname_list)
            self.show_image_file(random_image_fname_list)
            self.ui_main.test_image_text.setText(random_image[0])
            return random_image

        except FileNotFoundError:
            self.pop_up_message(
                "Please use 'single_prediction' folder for random image selection!"
            )

    def image_changer(self, path_of_image):
        pixmap = QPixmap(path_of_image)
        if not pixmap.isNull():
            self.ui_main.prediction_image_show.setPixmap(pixmap)
            self.ui_main.prediction_image_show.adjustSize()
            self.resize(pixmap.size())

    def bmp_converter(self, bmp_images):
        # Importing Library
        from PIL import Image

        for bmp_image in bmp_images:
            # Loading the image
            image = Image.open(bmp_image)

            # Specifying the RGB mode to the image
            image = image.convert("RGB")

            # Converting an image from PNG to JPG format
            image.save(bmp_image)

    def anomaly_scan_checker(self):
        self.info_screen.setText("> Scanning in progress")
        while True:
            infile_directory_path = (
                ext.get_current_workspace() + "/images/test_images/infile"
            )
            dirs = os.listdir(infile_directory_path)
            if dirs:
                self.full_scan_test()
                break
            time.sleep(1)

    def autonomous_find_binary_model_folder(self):
        """
        Select Model butonuna basıldığında kullanıcıdan model
        dosyalarının olduğu klasörü seçtirir.
        """
        model_fname = "binary_classification_model_2"
        model_fname = ext.str_splitter(model_fname)
        self.binary_model_folder_textbox.setText(model_fname)

    def autonomous_find_multi_model_folder(self):
        """
        Select Model butonuna basıldığında kullanıcıdan model
        dosyalarının olduğu klasörü seçtirir.
        """
        model_fname = "saved_trained_multi_model_12"
        model_fname = ext.str_splitter(model_fname)
        self.multi_model_folder_textbox.setText(model_fname)

    def full_scan_test(self):
        self.autonomous_find_binary_model_folder()
        self.autonomous_find_multi_model_folder()
        try:
            bmp_image_fname_list = []
            png_image_fname_list = []
            jpg_image_fname_list = []
            jpeg_image_fname_list = []

            dir_path = QFileDialog.getExistingDirectory(
                directory = ext.get_current_workspace() + "/images/test_images/infile"
            )

            if dir_path:
                outfile_path = ext.get_current_workspace() + "/images/test_images/outfile"
                dirs = os.listdir(outfile_path)

                if dirs:
                    for file in dirs:
                        target_file = outfile_path + "/" + file
                        os.remove(target_file)

            png_photos_from_file = fnmatch.filter(os.listdir(dir_path), "*.png*")
            jpg_photos_from_file = fnmatch.filter(os.listdir(dir_path), "*.jpg*")
            jpeg_photos_from_file = fnmatch.filter(os.listdir(dir_path), "*.jpeg*")
            bmp_photos_from_file = fnmatch.filter(os.listdir(dir_path), "*.bmp*")

            if bmp_photos_from_file:
                original_bmp_image_list = []
                for bmp_image in bmp_photos_from_file:
                    path_for_bmp_converter = dir_path + "/" + bmp_image
                    original_bmp_image_list.append(path_for_bmp_converter)
                self.bmp_converter(original_bmp_image_list)

                bmp_photo_numbers = len(bmp_photos_from_file)
                for i in range(bmp_photo_numbers):
                    image_path = dir_path + "/" + bmp_photos_from_file[i]
                    self.image_changer(image_path)
                    bmp_image_fname_list.append(image_path)
                    self.ui_main.test_image_text.setText(bmp_photos_from_file[i])
                    with open(
                        ext.get_current_workspace() + "/images/test_images/outfile/report.txt",
                        "a+",
                    ) as file1:
                        file1.write(
                            "\n" + "Test Image Name : " + bmp_photos_from_file[i] + "\n"
                        )
                    self.folder_prediction(image_path)
                    QtTest.QTest.qWait(500)
                print("{} tests are done!".format(bmp_photo_numbers))

            if png_photos_from_file:
                png_photo_numbers = len(png_photos_from_file)
                for i in range(png_photo_numbers):
                    image_path = dir_path + "/" + png_photos_from_file[i]
                    self.image_changer(image_path)
                    png_image_fname_list.append(image_path)
                    self.ui_main.test_image_text.setText(png_photos_from_file[i])
                    with open(
                        ext.get_current_workspace() + "/images/test_images/outfile/report.txt",
                        "a+",
                    ) as file1:
                        file1.write(
                            "\n" + "Test Image Name : " + png_photos_from_file[i] + "\n"
                        )
                    self.folder_prediction()
                    QtTest.QTest.qWait(500)
                print("{} tests are done!".format(png_photo_numbers))

            if jpg_photos_from_file:
                jpg_photo_numbers = len(jpg_photos_from_file)
                for i in range(jpg_photo_numbers):
                    image_path = dir_path + "/" + jpg_photos_from_file[i]
                    self.image_changer(image_path)
                    jpg_image_fname_list.append(image_path)
                    self.ui_main.test_image_text.setText(jpg_photos_from_file[i])
                    with open(
                        ext.get_current_workspace() + "/images/test_images/outfile/report.txt",
                        "a+",
                    ) as file1:
                        file1.write(
                            "\n" + "Test Image Name : " + jpg_photos_from_file[i] + "\n"
                        )
                    self.folder_prediction()
                    QtTest.QTest.qWait(500)
                print("{} tests are done!".format(jpg_photo_numbers))

            if jpeg_photos_from_file:
                jpeg_photo_numbers = len(jpeg_photos_from_file)
                for i in range(jpeg_photo_numbers):
                    image_path = dir_path + "/" + jpeg_photos_from_file[i]
                    self.image_changer(image_path)
                    jpeg_image_fname_list.append(image_path)
                    self.ui_main.test_image_text.setText(jpeg_photos_from_file[i])
                    with open(
                        ext.get_current_workspace() + "/images/test_images/outfile/report.txt",
                        "a+",
                    ) as file1:
                        file1.write(
                            "\n"
                            + "Test Image Name : "
                            + jpeg_photos_from_file[i]
                            + "\n"
                        )
                    self.folder_prediction()
                    QtTest.QTest.qWait(500)
                print("{} tests are done!".format(jpeg_photo_numbers))

            self.info_screen.setText("Full Scan Prediction Completed")
            now = str(datetime.datetime.now())

            process_folder_path = ext.get_current_workspace() + "/results/scanned_" + now
            infile_folder = ext.get_current_workspace() + "/images/test_images/infile"
            outfile_folder = ext.get_current_workspace() + "/images/test_images/outfile"

            shutil.copytree(
                infile_folder,
                process_folder_path,
                symlinks=False,
                ignore=None,
                copy_function=shutil.copy2,
                ignore_dangling_symlinks=False,
                dirs_exist_ok=False,
            )
            shutil.copytree(
                outfile_folder,
                process_folder_path,
                symlinks=False,
                ignore=None,
                copy_function=shutil.copy2,
                ignore_dangling_symlinks=False,
                dirs_exist_ok=True,
            )

            for file_name in os.listdir(infile_folder):
                file = infile_folder + "/" + file_name
                if os.path.isfile(file):
                    print("Deleting file:", file)
                    os.remove(file)

        except Exception as err:
            self.pop_up_message(err)

    def folder_prediction(self, image_path):
        """
        Start Prediction butonuna basıldığında modelin yüklenmesi
        ve test imageinin çözümlemesi gerçekleşir.
        """

        self.info_screen.setText("Prediction process is running...")
        # Get the workspace
        current_workspace = ext.get_current_workspace()

        # Load the model
        if (
            self.multi_model_folder_textbox.toPlainText() == ""
            and self.binary_model_folder_textbox.toPlainText() == ""
        ):  # If no model is selected
            self.pop_up_message("Please select a model folder!")
            return
        elif (
            self.multi_model_folder_textbox.toPlainText() != ""
            and self.binary_model_folder_textbox.toPlainText() == ""
        ):  # If multi-class model is selected
            loaded_model = tf.keras.models.load_model(
                current_workspace
                + "/models/"
                + self.multi_model_folder_textbox.toPlainText()
            )
            model_type = "multiclass"
        elif (
            self.binary_model_folder_textbox.toPlainText() != ""
            and self.multi_model_folder_textbox.toPlainText() == ""
        ):  # If binary-class model is selected
            loaded_model = tf.keras.models.load_model(
                current_workspace
                + "/models/"
                + self.binary_model_folder_textbox.toPlainText()
            )
            model_type = "binary"
        else:  # If both models are selected
            # self.pop_up_message("All models are loaded! Firstly, Binary-class prediction will be done.")
            model_type = "multi-process"
            loaded_binary_model = tf.keras.models.load_model(
                current_workspace
                + "/models/"
                + self.binary_model_folder_textbox.toPlainText()
            )
            loaded_multi_model = tf.keras.models.load_model(
                current_workspace
                + "/models/"
                + self.multi_model_folder_textbox.toPlainText()
            )
        # Get the test image name
        if self.ui_main.test_image_text.toPlainText() == "":
            self.pop_up_message("Please select a test image!")
        else:
            # test_image_fname = (
            #     current_workspace
            #     + "/single_prediction/"
            #     + self.ui_main.test_image_text.toPlainText()
            # )
            test_image_fname = image_path

        # Lock and Load the model
        if model_type != "multi-process":
            class_names = self.preprocess_the_data(model_type)

            # Predict the image
            if model_type == "multiclass":
                _, _, pred_results = self.prediction_function(
                    model=loaded_model,
                    filename=test_image_fname,
                    class_names=class_names,
                    model_type="multiclass",
                    shape=32,
                )
            elif model_type == "binary":
                _, _, pred_results = self.prediction_function(
                    model=loaded_model,
                    filename=test_image_fname,
                    class_names=class_names,
                    model_type="binary",
                    shape=128,
                )
            else:
                self.pop_up_message("Model Type Unknown!")

            # Send the prediction results to the info screen
            self.info_screen.setText("Prediction process completed...")
            self.prediction_results(pred_results)
        else:
            self.all_prediction_process(
                loaded_binary_model,
                loaded_multi_model,
                test_image_fname,
                current_workspace,
            )

    def start_prediction(self):
        """
        Start Prediction butonuna basıldığında modelin yüklenmesi
        ve test imageinin çözümlemesi gerçekleşir.
        """
        self.info_screen.setText("Prediction process is running...")
        # Get the workspace
        current_workspace = ext.get_current_workspace()

        # Load the model
        if (
            self.multi_model_folder_textbox.toPlainText() == ""
            and self.binary_model_folder_textbox.toPlainText() == ""
        ):  # If no model is selected
            self.pop_up_message("Please select a model folder!")
            return
        elif (
            self.multi_model_folder_textbox.toPlainText() != ""
            and self.binary_model_folder_textbox.toPlainText() == ""
        ):  # If multi-class model is selected
            loaded_model = tf.keras.models.load_model(
                current_workspace
                + "/models/"
                + self.multi_model_folder_textbox.toPlainText()
            )
            model_type = "multiclass"
        elif (
            self.binary_model_folder_textbox.toPlainText() != ""
            and self.multi_model_folder_textbox.toPlainText() == ""
        ):  # If binary-class model is selected
            loaded_model = tf.keras.models.load_model(
                current_workspace
                + "/models/"
                + self.binary_model_folder_textbox.toPlainText()
            )
            model_type = "binary"
        else:  # If both models are selected
            # self.pop_up_message("All models are loaded! Firstly, Binary-class prediction will be done.")
            model_type = "multi-process"
            loaded_binary_model = tf.keras.models.load_model(
                current_workspace
                + "/models/"
                + self.binary_model_folder_textbox.toPlainText()
            )
            loaded_multi_model = tf.keras.models.load_model(
                current_workspace
                + "/models/"
                + self.multi_model_folder_textbox.toPlainText()
            )
        # Get the test image name
        if self.ui_main.test_image_text.toPlainText() == "":
            self.pop_up_message("Please select a test image!")
        else:
            test_image_fname = (
                current_workspace
                + "/single_prediction/"
                + self.ui_main.test_image_text.toPlainText()
            )

        # Lock and Load the model
        if model_type != "multi-process":
            class_names = self.preprocess_the_data(model_type)

            # Predict the image
            if model_type == "multiclass":
                _, _, pred_results = self.prediction_function(
                    model=loaded_model,
                    filename=test_image_fname,
                    class_names=class_names,
                    model_type="multiclass",
                    shape=32,
                )
            elif model_type == "binary":
                _, _, pred_results = self.prediction_function(
                    model=loaded_model,
                    filename=test_image_fname,
                    class_names=class_names,
                    model_type="binary",
                    shape=128,
                )
            else:
                self.pop_up_message("Model Type Unknown!")

            # Send the prediction results to the info screen
            self.info_screen.setText("Prediction process completed...")
            self.prediction_results(pred_results)
        else:
            self.all_prediction_process(
                loaded_binary_model,
                loaded_multi_model,
                test_image_fname,
                current_workspace,
            )

    def all_prediction_process(
        self, binary_model, multi_model, test_image_fname, current_workspace
    ):
        """
        Binary ve Multi-class modeller tanımlandığında, sistem önce binary prediction yapması gerektiğini
        anlar. Binary prediction sonucunda resim hatalı çıkarsa multi-class prediction işlemi başlatılır.
        Normal çıkarsa süreç tamamlanır.
        """
        print("All Prediction Process Started")
        # self.image_changer(test_image_fname)

        # Öncelikle gelen resmin normal veya faulty olup olmadığı kontrol edilmelidir. Resim üzerinde standart
        # binary prediction işlemleri yapılır.

        ### BINARY PREDICTION ###
        # Binary prediction preprocessing data
        class_names = self.preprocess_the_data("binary")

        # Prediction Results for binary prediction
        _, _, pred_results = self.prediction_function(
            model=binary_model,
            filename=test_image_fname,
            class_names=class_names,
            model_type="binary",
            shape=128,
        )
        # Send all results to main panel
        self.prediction_results(pred_results)

        print("Binary Prediction Completed")  ## Info ekranına yazdırılacak.
        self.info_screen.setText("Binary Prediction Completed")
        ### END OF BINARY PREDICTION ###

        if float(pred_results[0].split("%")[-1]) < 50.0:  # eğer resim normal ise
            # self.image_changer(test_image_fname)
            print("This image is normal image. Prediction Completed!")
            # Bir önceki tekrarda faulty bir resim çıkmışsa, sonuç yüzdeleri ekranında o sonuçlar da görüntüleniyor.
            # Bu yüzden o kısımlar normal resim bulunduğunda sıfırlanmalı.
            self.old_results_cleaner()

        else:  # Eğer resim faulty ise, multi-class prediction işlemleri başlatılır.
            print("This image is faulty image. Multi-class prediction started...")
            self.info_screen.setText(
                "This image is faulty image. Multi-class prediction started..."
            )

            ### MULTI-CLASS PREDICTION ###
            # Multiclass prediction preprocessing data
            class_names = self.preprocess_the_data("multiclass")

            # Prediction Results for multiclass prediction
            _, _, pred_results = self.prediction_function(
                model=multi_model,
                filename=test_image_fname,
                class_names=class_names,
                model_type="multiclass",
                shape=32,
            )
            # Send all results to main panel
            self.prediction_results(pred_results)
            print("Multiclass Prediction Completed")  ## Info ekranına yazdırılacak.
            self.info_screen.setText("Multiclass Prediction Completed")
            ### END OF MULTICLASS PREDICTION ###

        # return

    def prediction_results(self, pred_results):
        """
        Prediction sonuçlarını ekrandaki progress bar'larda görüntüler.
        """
        for i in range(len(pred_results)):
            # Get class name
            class_name = pred_results[i].split(":")[0]
            # Get prediction result
            pred_val = pred_results[i].split("%")[-1]
            # Set the class' progress bar
            self.findChild(QProgressBar, class_name + "_progressbar").setValue(
                float(pred_val)
            )

    def preprocess_the_data(self, model_type):
        """
        Alınan test resiminin hangi prediction yöntemi kullanıldığına göre sınıf
        isimleri ayarlanır.
        """
        if model_type == "binary":
            class_names = ["faulty", "normal"]
        elif model_type == "multiclass":
            class_names = [
                "dilation",
                "erosion",
                "gaussian",
                "gradient",
                "poisson",
                "saltpepper",
            ]

        return class_names

    def prediction_function(self, model, filename, class_names, model_type, shape):
        """
        Imports an image located at filename, makes a prediction
        with model and plots the image with the predicted class
        as the title.
        """
        # Import the target image and preprocess it
        pred_results = []
        img, _ = self.image_shape_fixer(filename, shape)

        # Make a prediction
        pred = model.predict(tf.expand_dims(img, axis=0))

        # Bu kısım, predict edilen resmin hangi hataya ait olduğunu
        # tüm hataların yüzdelik olasığına göre görmemizi sağlar
        if model_type == "multiclass":
            print(class_names)
            for i in range(len(pred[0])):
                prediction_val = float(pred[0][i]) * 100
                print(
                    class_names[i] + ": %" + "{:.2f}".format(round(prediction_val, 2))
                )
                pred_results.append(
                    class_names[i] + ": %" + "{:.2f}".format(round(prediction_val, 2))
                )
        elif model_type == "binary":
            prediction_val = float(pred[0][0]) * 100
            print(
                class_names[0] + ": %" + "{:.2f}".format(100 - round(prediction_val, 2))
            )  # faulty pred rate
            print(
                class_names[1] + ": %" + "{:.2f}".format(round(prediction_val, 2))
            )  # normal pred rate

            # Pred Results
            pred_results.append(
                class_names[0] + ": %" + "{:.2f}".format(100 - round(prediction_val, 2))
            )
            pred_results.append(
                class_names[1] + ": %" + "{:.2f}".format(round(prediction_val, 2))
            )

        # Add in logic for multi-class
        if len(pred[0]) > 1:
            pred_class = class_names[tf.argmax(pred[0])]
        else:
            # Get the predicted class
            pred_class = class_names[int(tf.round(pred[0]))]

        # self.prediction_label.setEnabled(True)
        self.pred_result_text_screen.setText(pred_class)

        TEST_IMAGE_NAME = self.ui_main.test_image_text.toPlainText()
        PREDICTION_RESULT = self.ui_main.prediction_result_text_screen.text()

        if PREDICTION_RESULT != "faulty" and PREDICTION_RESULT != "normal":
            with open(
                ext.get_current_workspace() + "/images/test_images/outfile/report.txt",
                "a+",
            ) as file1:
                prediction_result_for_report = (
                    "Fault Type : " + PREDICTION_RESULT + "\n"
                )
                file1.write(prediction_result_for_report)

        if PREDICTION_RESULT == "normal":
            with open(
                ext.get_current_workspace() + "/images/test_images/outfile/report.txt",
                "a+",
            ) as file1:
                prediction_result_for_report = (
                    "Prediction Result : " + PREDICTION_RESULT + "\n"
                )
                file1.write(prediction_result_for_report)
                prediction_result_for_report = "Fault Type : None" + "\n"
                file1.write(prediction_result_for_report)

        if PREDICTION_RESULT == "faulty":
            with open(
                ext.get_current_workspace() + "/images/test_images/outfile/report.txt",
                "a+",
            ) as file1:
                prediction_result_for_report = (
                    "Prediction Result : " + PREDICTION_RESULT + "\n"
                )
                file1.write(prediction_result_for_report)

        return img, pred_class, pred_results

    def old_results_cleaner(self):
        """
        Progress barlarını temizler.
        """
        class_names = [
            "dilation",
            "erosion",
            "gaussian",
            "gradient",
            "poisson",
            "saltpepper",
        ]
        for i in range(len(class_names)):
            self.findChild(QProgressBar, class_names[i] + "_progressbar").setValue(
                float(0)
            )

    @classmethod
    def pop_up_message(cls, msg):
        """
        It is the function that publishes the error messages in the tool as a pop up.
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(str(msg))
        msg_box.setWindowTitle("Error")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    @classmethod
    def pop_up_info_message(cls, msg):
        """
        It is the function that publishes the info messages in the tool as a pop up.
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(str(msg))
        msg_box.setWindowTitle("Info")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def to_be_declared_msg(self):
        self.pop_up_info_message("This section will be added!")

    @classmethod
    def usage_info(cls):
        """
        It is the function where the Help button is defined.
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setInformativeText("How can I use this tool?\n\n")
        msg_box.setDetailedText(
            """Anomali tespit aracını kullanmak için:
        - Öncelikle hazırlanmış bir modeli yüklemeniz gerekir, eğer binary classification ile hazırlanmış bir model ile test yapılacaksa "Binary Model Name" kısmındaki "Find Model" butonu ile modelinizi yükleyin. Multiclass model ise aynı işlemi "Multi Model Name" kısmında yapın.
        - Eğer her iki modele de sahipseniz ikisini de yükledikten sonra prediction işlemini başlatın.
        - "Test Image Name" kısmından tahmin yaptıracağınız resmi seçin. 
        - "Random Img. Select" özelliğini kullanmak isterseniz, program klasöründe "single_prediction" isimli bir klasör içerisinde tahmin yapılacak resimleriniz bulunmalıdır.
        - Model ve Test resmi yüklemeleri tamamlandıktan sonra tahmin işlemini "Start Prediction" butonu ile gerçekleştirebilirsiniz.
        - Yaptığınız işlemleri ve sonuçlarını "Save Results" butonu ile kaydedebilirsiniz.
        """
        )
        msg_box.setWindowTitle("Help")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()


# Initialize the app
app = QApplication(sys.argv)
Ui_MainWindow = FIAnomalyDetector()
app.exec_()
