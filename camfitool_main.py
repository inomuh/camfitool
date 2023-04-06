# -*- coding: utf-8 -*-,
"""
Camera Fault Injection Tool (CamFITool)
-----------------------------------------------
This tool is a simple interface that allows injection of image faults
into robot cameras. Thanks to this interface, you can create new image
libraries by injecting the fault types you have determined, both real-time
to ROS cameras, and to the image libraries previously
recorded by these cameras.
"""
__author__ = "Alim Kerem Erdogmus"
__version__ = "v2.0.0"
__email__ = "kerem.erdogmus@inovasyonmuhendislik.com"
__status__ = "Beta"

import sys
import os
import time
import datetime
from PyQt5 import QtWidgets

import ui_interface as Ui

from offline_fault_injector_ui import main as ofi
from realtime_fault_injector_ui import RealtimeFaultInjector as rfi

import extras as ext

class MainWindow(QtWidgets.QMainWindow):
    """
    CamFITool Interface MainWindow Class
    """

    def __init__(self):
        self.normal_image_folder = None
        self.fi_image_folder = None
        self.fi_freq = None
        self.fi_plan = None
        self.fi_type = None
        self.fault_type = None
        self.fault_rate = None
        self.fault_imp_rate = 100  # default
        self.robot_camera_type = None
        self.ros_cam_topic = None
        self.ros_cam_fi_freq = None
        # For checking last process, we need last process logs and fi image file name
        self.last_fi_image_list = None
        self.last_fi_image_folder = None
        self.repeated_fi_process = False
        self.repeated_process_lock = False
        self.normal_image_list = None
        self.last_fi_logname = None

        QtWidgets.QMainWindow.__init__(self)
        self.ui_int = Ui.Ui_MainWindow()
        self.ui_int.setupUi(self)
        self.show()

        self.setWindowIcon(Ui.QtGui.QIcon(":icons/imfit_logo.png"))
        self.setWindowTitle("Camera Fault Injection Tool")

        QtWidgets.QSizeGrip(self.ui_int.size_grip)

        self.ui_int.fi_type_combobox.addItems(
            ["--Select one--", "Offline", "Real-time"])
        self.ui_int.fault_type_combobox.addItems(
            ["--Select one--", "Salt&Pepper", "Gaussian",
                "Poisson", "Erosion", "Dilation", "Gradient"])

        self.ui_int.fi_type_combobox.currentTextChanged.connect(self.real_time_options)
        self.ui_int.robot_camera_combobox.currentTextChanged.connect(self.ros_camera_options)
        self.ui_int.fault_rate_textbrowser.setPlainText("0")
        self.ui_int.fault_rate_slider.valueChanged.connect(self.fault_rate_slider)
        self.ui_int.fault_imp_rate_textbrowser.setPlainText("100")
        self.ui_int.fault_imp_rate_slider.valueChanged.connect(self.fault_imp_rate_slider)
        self.ui_int.find_image_file_button.clicked.connect(self.find_image_file)
        self.ui_int.find_fi_file_button.clicked.connect(self.find_fi_image_folder)
        self.ui_int.apply_fault_button.clicked.connect(self.apply_fault)
        self.ui_int.save_fi_plan_button.clicked.connect(self.save_fi_plan)
        self.ui_int.show_fi_plan_details_button.clicked.connect(self.details_fi_list_func)
        self.ui_int.progressBar.setValue(0)

        ### MENUS ###
        self.ui_int.actionNew.triggered.connect(ext.reset_button_function)
        self.ui_int.actionSave_FI_Plan.triggered.connect(self.save_fi_plan)
        self.ui_int.actionQuit.triggered.connect(sys.exit)
        self.ui_int.actionUsageInfo.triggered.connect(self.help_section)
        self.ui_int.actionROS_Camera.triggered.connect(lambda: self.robot_camera_live(self.robot_camera))
        self.ui_int.actionGo_Anomaly_Detector.triggered.connect(ext.go_fiad_app_func)
        # Will be added
        self.ui_int.actionCamFITool.triggered.connect(ext.camfitool_web)
        self.ui_int.actionVALU3S.triggered.connect(ext.valu3s_web)
        self.ui_int.actionIMTGD.triggered.connect(ext.imtgd_web)
        ######


        # When the Robot Camera button is pressed, the ros node in
        # the robot_camera variable is monitored.
        self.robot_camera = None
        self.publish_camera = None

        # When the interface is opened, the default normal and faulty picture
        # folders and the fi plan list are automatically loaded.
        self.starter_folder_indexes()

        # The part where fonts and sizes of ROS Cam Text and ROS Stream Freq tabs are set
        self.default_robot_camera_configs()

        self.ui_int.info_text.setText("Welcome to Camera Fault Injection Tool v2.0")
        self.show()

    def starter_folder_indexes(self):
        """
        It is the function in which the module names and standard locations of the normal
        and incorrect image folders are defined as the "folder_module" and "folder_location"
        variables.
        """
        folder_list = [
            [
                "image_file",
                str(ext.get_current_workspace()) + "/images/normal_image_folders/",
            ],
            [
                "fi_file",
                str(ext.get_current_workspace()) + "/images/fault_image_folders/",
            ],
        ]

        for i, j in folder_list:
            self.open_default_folders(i, j)

        self.update_fi_list_func()

    def open_default_folders(self, folder_module, folder_location):

        """
        It is the function that brings the default folders to the interface in
        accordance with the module and location information coming from
        the starter_folder_indexes function.
        """
        model = QtWidgets.QFileSystemModel()
        model.setRootPath(folder_location)

        if folder_module == "fi_file":
            self.ui_int.fi_file_tree.setModel(model)
            self.ui_int.fi_file_tree.setRootIndex(model.index(folder_location))
            self.ui_int.fi_file_tree.setSortingEnabled(True)
            self.ui_int.fi_file_tree.hideColumn(1)
            self.ui_int.fi_file_tree.hideColumn(2)
            self.ui_int.fi_file_tree.setColumnWidth(0, 200)
        else:
            self.ui_int.image_file_tree.setModel(model)
            self.ui_int.image_file_tree.setRootIndex(model.index(folder_location))
            self.ui_int.image_file_tree.setSortingEnabled(True)
            self.ui_int.image_file_tree.hideColumn(1)
            self.ui_int.image_file_tree.hideColumn(2)
            self.ui_int.image_file_tree.setColumnWidth(0, 200)

    def find_image_file(self):
        """
        It is the function that selects the folder where the normal pictures
        are located, to which the fault will be applied.
        """

        self.normal_image_folder = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Normal Images Directory",
                str(ext.get_current_workspace()) + "images/normal_image_folders/",
            )
        )

        model = QtWidgets.QFileSystemModel()
        model.setRootPath(self.normal_image_folder)

        self.ui_int.image_file_tree.setModel(model)
        self.ui_int.image_file_tree.setRootIndex(model.index(self.normal_image_folder))
        self.ui_int.image_file_tree.setSortingEnabled(True)
        self.ui_int.image_file_tree.hideColumn(1)
        self.ui_int.image_file_tree.hideColumn(2)
        self.ui_int.image_file_tree.setColumnWidth(0, 200)

    def find_fi_image_folder(self):
        """
        It is the function that selects the folder where the images with the fault will be saved.
        """

        self.fi_image_folder = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Faulty Images Directory",
                str(ext.get_current_workspace()) + "images/fault_image_folders/",
            )
        )

        model = QtWidgets.QFileSystemModel()
        model.setRootPath(self.fi_image_folder)

        self.ui_int.fi_file_tree.setModel(model)
        self.ui_int.fi_file_tree.setRootIndex(model.index(self.fi_image_folder))
        self.ui_int.fi_file_tree.setSortingEnabled(True)
        self.ui_int.fi_file_tree.hideColumn(1)
        self.ui_int.fi_file_tree.hideColumn(2)
        self.ui_int.fi_file_tree.setColumnWidth(0, 200)

    def update_fi_list_func(self):
        """
        It is the function where the Update FIP List button is defined.
        When new fi plans are saved, they do not go directly to FI Plans.
        It is possible to update the list there after each new record with this button.
        """
        onlyfiles_location = str(ext.get_current_workspace()) + "/fi_plans"

        model = QtWidgets.QFileSystemModel()
        model.setRootPath(onlyfiles_location)

        self.ui_int.fi_plan_tree.setModel(model)
        self.ui_int.fi_plan_tree.setRootIndex(model.index(onlyfiles_location))
        self.ui_int.fi_plan_tree.setSortingEnabled(True)
        self.ui_int.fi_plan_tree.hideColumn(1)
        self.ui_int.fi_plan_tree.hideColumn(2)
        self.ui_int.fi_plan_tree.setColumnWidth(0, 200)

    def real_time_options(self):
        """
        It is the function where the Fault Injection Type menu is set.
        When real-time is selected, the camera types of the robot
        (Robot Camera option) become selectable.
        """

        if self.ui_int.fi_type_combobox.currentText() == "Real-time":
            self.ui_int.robot_camera_combobox.clear()
            self.ui_int.robot_camera_combobox.addItems(["--Select one--", "ROS Camera"])
            # self.ui_int.randomize_check.setText("CV2 Screen")
            self.ui_int.randomize_check.setEnabled(False)

            # Closing all image folder selection menus
            self.ui_int.image_file_tree.setEnabled(False)
            self.ui_int.fi_file_tree.setEnabled(False)
            self.ui_int.fault_imp_rate_frame.setEnabled(False)
            self.ui_int.fault_imp_rate_label.setEnabled(False)
            # Find Image File Button disabling
            self.ui_int.find_image_file_button.setEnabled(False)
            self.ui_int.find_image_file_button.setStyleSheet(
                "background-color: rgb(255, 255, 255);" "color: rgb(222, 222, 222);"
            )
            # Find FI Image File Button disabling
            self.ui_int.find_fi_file_button.setEnabled(False)
            self.ui_int.find_fi_file_button.setStyleSheet(
                "background-color: rgb(255, 255, 255);" "color: rgb(222, 222, 222);"
            )

        elif self.ui_int.fi_type_combobox.currentText() == "Offline":
            self.ui_int.robot_camera_combobox.clear()
            self.ui_int.robot_camera_combobox.addItems(["None"])
            # self.ui_int.randomize_check.setText("Randomize")
            self.ui_int.randomize_check.setEnabled(True)

            # Opening all image folder selection menus
            self.ui_int.image_file_tree.setEnabled(True)
            self.ui_int.fi_file_tree.setEnabled(True)
            self.ui_int.fault_imp_rate_frame.setEnabled(True)
            self.ui_int.fault_imp_rate_label.setEnabled(True)

            # Find Image File Button enabling
            self.ui_int.find_image_file_button.setEnabled(True)
            self.ui_int.find_image_file_button.setStyleSheet(
                "background-color: rgb(255, 255, 255);" "color: rgb(0, 0, 0);"
            )
            # Find FI Image File Button enabling
            self.ui_int.find_fi_file_button.setEnabled(True)
            self.ui_int.find_fi_file_button.setStyleSheet(
                "background-color: rgb(255, 255, 255);" "color: rgb(0, 0, 0);"
            )

        else:
            self.ui_int.robot_camera_combobox.clear()
            self.ui_int.robot_camera_combobox.addItems(["None"])

    def ros_camera_options(self):
        """
        It is the function where the Robot Camera menu is set. When ROS Camera is selected,
        a text bar will be activated where the user can enter the name of the ROS camera
        topic that is requested to apply a realtime error. When None is selected,
        this part disappears.
        """
        if self.ui_int.robot_camera_combobox.currentText() == "ROS Camera":

            self.ui_int.ros_cam_topic_label.setEnabled(True)
            self.ui_int.ros_cam_topic_text.setEnabled(True)
            self.ui_int.ros_cam_fi_freq_label.setEnabled(True)
            self.ui_int.ros_cam_fi_freq_text.setEnabled(True)
            self.ui_int.ros_cam_topic_text.setReadOnly(False)
            self.ui_int.ros_cam_fi_freq_text.setReadOnly(False)
            self.ui_int.ros_cam_topic_label.setText("ROS Cam. Topic  ")

            self.ui_int.ros_cam_topic_text.setText("Enter here ROS Camera Topic name ")
            self.ui_int.ros_cam_fi_freq_label.setText("Cam. Stream Freq (Hz)  ")
            self.ui_int.ros_cam_fi_freq_text.setText(
                "Enter here ROS Stream Frequency value"
            )
            self.robot_camera = self.ui_int.ros_cam_topic_text.toPlainText()
            self.fi_freq = self.ui_int.ros_cam_fi_freq_text.toPlainText()

            # Edits fonts and font size when editing Robot Camera configurations.
            self.ui_int.ros_cam_topic_text.textChanged.connect(
                self.update_ros_cam_topic_config
            )
            self.ui_int.ros_cam_fi_freq_text.textChanged.connect(
                self.update_ros_cam_fi_freq_config
            )

        else:
            self.ui_int.ros_cam_topic_label.setEnabled(False)
            self.ui_int.ros_cam_topic_text.setEnabled(False)
            self.ui_int.ros_cam_fi_freq_label.setEnabled(False)
            self.ui_int.ros_cam_fi_freq_text.setEnabled(False)
            self.ui_int.ros_cam_topic_text.setReadOnly(True)
            self.ui_int.ros_cam_fi_freq_text.setReadOnly(True)
            self.ui_int.ros_cam_topic_label.setText(" ")
            self.ui_int.ros_cam_fi_freq_label.setText(" ")
            self.ui_int.ros_cam_topic_text.clear()
            self.ui_int.ros_cam_fi_freq_text.clear()
            self.default_robot_camera_configs()

    def apply_fault_button_func(self, process):
        """
        The Apply Fault button is disabled when the fault application process
        starts. After the fault handling is complete, the button is returned
        to working condition. When the fault application is complete, the Apply
        Fault button is restored.
        """
        if process is True:
            self.ui_int.apply_fault_button.setEnabled(False)
            self.ui_int.apply_fault_button.setStyleSheet(
                "background-color: rgb(255, 255, 255);" "color: rgb(0, 0, 0);"
            )
            self.ui_int.apply_fault_button.setText("Processing")
            self.ui_int.apply_fault_button.setIcon(
                Ui.QtGui.QIcon(":icons/cil-external-link.png")
            )
        else:
            self.ui_int.apply_fault_button.setDisabled(False)
            self.ui_int.apply_fault_button.setStyleSheet(
                "background-color: rgb(6, 37, 98);" "color: rgb(255, 255, 255);"
            )
            self.ui_int.apply_fault_button.setText("Apply Fault")
            self.ui_int.apply_fault_button.setIcon(
                Ui.QtGui.QIcon(":icons/cil-cloud-upload.png")
            )

    def apply_fault(self):
        """
        It is the function where the Apply Fault button is run. The fault suitable for the
        features selected in the Camera Fault Configuration section is applied to the images
        in the folder selected in the Normal Image Folders section, and it starts the recording
        of these faulty images to the folder selected in the FI Image Folder section.
        """
        #### OFFLINE FAULT INJECTION PART ####
        if self.ui_int.fi_type_combobox.currentText() == "Offline":
            print("Processing..")
            # The Apply Fault button is disabled when the fault application process
            # starts. After the fault handling is complete, the button is returned
            # to working condition.

            self.apply_fault_button_func(True)

            # This line will be removed when the plan is selected from the
            # saved plan list and the application is added.
            plan_from_list = False
            if plan_from_list:
                try:
                    self.ui_int.info_text.clear()
                    with open(
                        str(ext.get_current_workspace()) + "/fi_plans/" + self.fi_plan,
                        "r",
                        encoding="utf-8",
                    ) as fi_plan_file:
                        self.ui_int.info_text.setText(
                            "FI Plan Applying ...\n-----------------\n"
                            + fi_plan_file.read()
                        )
                except IndexError:
                    self.pop_up_message(
                        'Please choose one fault injection plan from "FI Plans"!'
                    )
                    ext.error_log_creator(IndexError)
                else:
                    if self.ui_int.randomize_check.isChecked():
                        print("randomized")
                    else:
                        print("unrandomized")
            else:
                #### APPLY FAULT SECTION ############
                self.info_temp()
                file_path = ext.get_current_workspace()
                ## The folder that was clicked in the Normal and Faulty images table is processed.
                # Addresses should change, the location of the folder we choose
                # should come automatically.

                try:
                    self.normal_image_folder = (
                        str(file_path)
                        + "/images/normal_image_folders/"
                        + str(self.ui_int.image_file_tree.selectedIndexes()[0].data())
                        + "/"
                    )
                    self.fi_image_folder = (
                        str(file_path)
                        + "/images/fault_image_folders/"
                        + str(self.ui_int.fi_file_tree.selectedIndexes()[0].data())
                        + "/"
                    )
                    randomized = self.ui_int.randomize_check.isChecked()

                    ## Check Last FI Process / Repeated Fault Inj Process####
                    #######################################################

                    if self.repeated_fi_process is True:
                        print("--repeated")
                        """
                        Tekrarli hata enj. uygulandiginda last_fi_image_list adinda bir degisken
                        de ofi'ye gönderilir, bu degisken bir önceki islemde hata basilmis
                        resimlerin isimlerini icerir.
                        """
                        if self.repeated_process_lock is False:
                            resource, count, fi_image_name_list = ofi(
                                self.normal_image_folder,
                                self.fi_image_folder,
                                self.fault_type,
                                self.fault_rate,
                                randomized,
                                int(self.fault_imp_rate),
                                self.last_fi_image_list,
                            )
                            # normal_image_folder -> new_normal_img_fold
                            self.repeated_process_lock = True
                        else:
                            if self.last_fi_image_folder == self.fi_image_folder:
                                self.pop_up_message(
                                    "You can only two repeated fi process in"
                                    + " same fi output folder. Please use different "
                                    + "'FI Image Folder'."
                                )
                                self.apply_fault_button_func(False)
                                print("Not Completed..Change FI Output folder.")
                            else:
                                self.ui_int.info_text.setPlainText(
                                    "You changed output folder."
                                    + " Click Apply Fault button again for FI!"
                                )
                                self.repeated_process_lock = False
                            return None
                    else:
                        resource, count, fi_image_name_list = ofi(
                            self.normal_image_folder,
                            self.fi_image_folder,
                            self.fault_type,
                            self.fault_rate,
                            randomized,
                            int(self.fault_imp_rate),
                            None,
                        )

                    #### END APPLY FAULT SECTION ###############
                    # When the Randomize option is active, the system generates a random
                    # number of faulty images. Faulty images are randomly selected.

                    if randomized:
                        self.progress_counter(count)
                        self.ui_int.info_text.setPlainText(
                            resource
                            + str("\nFault Injected Files:\n")
                            + str(fi_image_name_list)
                        )
                    else:
                        self.progress_counter(count)
                        self.ui_int.info_text.setPlainText(resource)

                    # For logging faulty images name list
                    self.faulty_image_list_saver(
                        self.fi_image_folder, fi_image_name_list
                    )

                except IndexError:
                    self.pop_up_message(
                        "Please choose one Normal and one "
                        + "Fault image folders from Folder Selection Section on the left side."
                    )
                    ext.error_log_creator(IndexError)
                except Exception as error_msg:
                    self.pop_up_message(
                        "Something wrong! You should look logs file for details."
                    )
                    ext.error_log_creator(error_msg)

            print("Completed..")

            # When the fault application is complete, the Apply Fault button is restored.
            self.apply_fault_button_func(False)

        #### END OF THE OFFLINE FAULT INJECTION PART ####

        #### REALTIME FAULT INJECTION PART ####
        elif self.ui_int.fi_type_combobox.currentText() == "Real-time":
            print("Processing..")
            self.ui_int.info_text.setText("Fault injecting to the ROS camera stream...")
            self.robot_camera = self.ui_int.ros_cam_topic_text.toPlainText()
            self.pop_up_message(
                "This process will be broken this interface. " + "This will be fixed."
            )

            # This line will be removed when the plan is selected from the saved plan
            # list and the application is added.
            plan_from_list = False

            if plan_from_list:
                try:
                    self.ui_int.info_text.clear()
                    with open(
                        str(ext.get_current_workspace()) + "/fi_plans/" + self.fi_plan,
                        "r",
                        encoding="utf-8",
                    ) as fi_plan_file:
                        self.ui_int.info_text.setText(
                            "FI Plan Applying ...\n-----------------\n"
                            + fi_plan_file.read()
                        )
                except IndexError:
                    self.pop_up_message(
                        'Please choose one fault injection plan from "FI Plans"!'
                    )
                    ext.error_log_creator(IndexError)
            else:
                self.info_temp()
                cv2_screen = False  # DEVELOPING

                self.publish_camera = self.robot_camera  ## Will be changed.

                try:
                    # If the user enters str instead of an int value, the system will
                    # give an error message, apply_fault will not work.
                    self.fi_freq = int(self.ui_int.ros_cam_fi_freq_text.toPlainText())
                except ValueError:
                    self.pop_up_message("Please enter a valid frequency value!")
                    ext.error_log_creator(ValueError)
                else:
                    # Realtime FI process
                    rfi(
                        self.robot_camera,
                        self.publish_camera,
                        self.fault_type,
                        self.fault_rate,
                        self.fi_freq,
                        cv2_screen,
                    )

        else:
            self.pop_up_message(
                "Something is wrong! You should check your fault configuration."
            )
            ext.error_log_creator(
                "Fault configuration error! It may be missing or created "
                + "incorrectly. Fill in all the configurations and try again."
            )

        #### END OF THE REALTIME FAULT INJECTION PART ####

    def progress_counter(self, count):
        """
        It is the function that controls the progress bar.
        """
        self.ui_int.progressBar.setFormat(" ")
        for i in range(count):
            counter = (i / count) * 100 + 1
            self.ui_int.progressBar.setValue(int(counter))
            time.sleep(count / 10000)
        # counter değeri bazı durumlarda 100'e ulaşmadığı için
        # bu kontrol ile progressbar tamamlanır.
        if (
            counter != 100
        ):
            self.ui_int.progressBar.setValue(100)
        self.ui_int.progressBar.setFormat("Completed")

    def camera_fault_config(self):
        """
        It is the function that saves the properties defined in the Camera Fault Configuration menu.
        """

        self.robot_camera_type = self.ui_int.robot_camera_combobox.currentText()
        self.fi_type = self.ui_int.fi_type_combobox.currentText()
        self.fault_type = self.ui_int.fault_type_combobox.currentText()

    def folder_info_temp(self):
        """This function takes fault injection configuration infos"""
        self.fi_type = self.ui_int.fi_type_combobox.currentText()
        self.robot_camera_type = self.ui_int.robot_camera_combobox.currentText()
        self.fault_type = self.ui_int.fault_type_combobox.currentText()

        if self.fi_type == "Offline":
            try:
                self.normal_image_folder = (
                    str(ext.get_current_workspace())
                    + "/images/normal_image_folders/"
                    + str(self.ui_int.image_file_tree.selectedIndexes()[0].data())
                    + "/"
                )
                # Normal img kütüphanesindeki resimlerin isimleri kaydedilir.
                self.normal_image_list = ext.read_image_list(self.normal_image_folder)
            except IndexError:
                self.pop_up_message(
                    "Please select a fault type from the fault type combobox."
                )
                ext.error_log_creator(IndexError)

    def info_temp(self):
        # This function will be updated.
        """
        It is the function that writes the properties defined in the Camera Fault Configuration menu
        to the Info section (from folder_info_temp func). For this, it saves the configs in a
        temporary file called temp.txt, writes the revised info from that file to the Info tab and
        deletes the temp file.
        """
        self.folder_info_temp()
        try:
            if self.fi_type == "Offline":
                with open("temp.txt", "a", encoding="utf-8") as temp_file:
                    temp_file.write("Fault Inj. Type: " + self.fi_type)
                    temp_file.write("\nFault Type: " + self.fault_type)
                    temp_file.write("\nFault Rate: " + self.fault_rate + "%")
                    temp_file.write("\nRobot Camera: " + self.robot_camera_type)
                    temp_file.write("\nFault Value: ")
                    # tekrarli fi islemi tespit edilirse hata uygulanmasi gereken normal
                    # resim sayisinin yeniden düzenlenmesi gerekir
                    # bir önceki islemde hata uygulanmis resimlere tekrar hata uygulanmamali.
                    if self.repeated_fi_process:
                        total_normal_image, total_faulty_image = self.repeated_fi()
                        temp_file.write("\nRepeated FI Process\n")
                    else:
                        total_normal_image = len(
                            self.normal_image_list
                        )  # normal resim sayisi
                        total_faulty_image = int(
                            int(total_normal_image) * int(self.fault_imp_rate) / 100
                        )
                        # hata uygulanacak resim sayisi

                    temp_file.write(
                        str(total_faulty_image) + "/" + str(total_normal_image)
                    )
            else:
                self.ros_cam_topic = self.ui_int.ros_cam_topic_text.toPlainText()
                self.ros_cam_fi_freq = self.ui_int.ros_cam_fi_freq_text.toPlainText()

                with open("temp.txt", "a", encoding="utf-8") as temp_file:
                    temp_file.write("Robot Camera: " + self.robot_camera_type)
                    temp_file.write("\nROS Camera Topic: " + self.ros_cam_topic)
                    temp_file.write("\nROS Camera FI Stream Freq: " + self.ros_cam_fi_freq + "Hz")
                    temp_file.write("\nFault Inj. Type: " + self.fi_type)
                    temp_file.write("\nFault Type: " + self.fault_type)
                    temp_file.write("\nFault Rate: " + self.fault_rate + "%")

        except AttributeError:
            self.pop_up_message("Fault Rate Missing!")
            ext.error_log_creator(AttributeError)

        except TypeError:
            self.pop_up_message("Fault Rate Missing!")
            ext.error_log_creator(TypeError)

        else:
            if self.fi_type == "Offline":
                if self.ui_int.randomize_check.isChecked():
                    with open("temp.txt", "a", encoding="utf-8") as temp_file:
                        temp_file.write("\nRandom FI: True")
                elif self.ui_int.randomize_check.isChecked() is False:
                    with open("temp.txt", "a", encoding="utf-8") as temp_file:
                        temp_file.write("\nRandom FI: False")
                else:
                    pass

            temp_file.close()
            with open("temp.txt", "r", encoding="utf-8") as temp_file:
                self.ui_int.info_text.setText(temp_file.read())
            os.remove("temp.txt")

    def save_fi_plan(self):
        """
        It is the function where the Save FI Plan button is defined. Saves the fault
        properties defined in the Camera Fault Config menu to a selected .txt file.
        After this registration process, it publishes the confirmation message in the
        Info tab. (The registration system made in this section will be arranged with
        a .json extension later.)
        """
        self.info_temp()

        try:
            # S_File will get the directory path and extension.
            save_file = Ui.QtWidgets.QFileDialog.getSaveFileName(
                None,
                "Save FI Plan",
                str(ext.get_current_workspace()) + "/fi_plans/fi_plan",
                "Text Files (*.txt)",
            )

            # This will let you access the test in your QTextEdit
            save_text = self.ui_int.info_text.toPlainText()

            # This will prevent you from an error if pressed cancel on file dialog.
            if save_file[0]:
                # Finally this will Save your file to the path selected.
                with open(save_file[0], "w", encoding="utf-8") as temp_file:
                    date = datetime.datetime.now()
                    temp_file.write("Created: " + str(date.ctime()))
                    temp_file.write("\n----------------------------------\n")
                    temp_file.write(save_text)

            self.ui_int.info_text.setText(
                "FI Plan Saved! For Details any Plan, "
                + "Please Choose One of Them from 'FI Plans' Section and click "
                + "'Show FIP Details' button!"
            )

        except AttributeError:
            self.pop_up_message("Fault Rate Missing!")
            ext.error_log_creator(AttributeError)

        self.update_fi_list_func()

    @classmethod
    def pop_up_message(cls, msg):
        """
        It is the function that publishes the error messages in the tool as a pop up.
        """
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.setText(msg)
        msg_box.setWindowTitle("Warning")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec()

    @classmethod
    def about_section(cls):
        """
        It is the function where the About button is defined.
        """
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setText(
            "Camera Fault Injection Tool, Oct 2021\n"
            + "For More Information, Contact kerem.erdogmus@inovasyonmuhendislik.com."
        )
        msg_box.setWindowTitle("About")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec()

    @classmethod
    def help_section(cls):
        """
        It is the function where the Help button is defined.
        """
        url = "https://github.com/inomuh/camfitool/wiki"
        ext.open_website(url)

        """
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setInformativeText("Welcome to Camera Fault Injection Tool v2.0\n\n")
        msg_box.setDetailedText("TBD") # read text ile ekle.
        msg_box.setWindowTitle("Help")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec()
        """
    @classmethod
    def pop_up_info_message(cls, msg):
        """
        It is the function that publishes the info messages in the tool as a pop up.
        """
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setText(str(msg))
        msg_box.setWindowTitle("Info")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec()

    def fault_rate_slider(self):
        """
        It is the function that allows setting the Fault Rate value in the Camera Fault
        Configuration menu. When the slider there is scrolled, the desired rate value is
        displayed in the box. Box overwriting is not allowed (this feature can be added
        later, but the slider must be edited to react accordingly.)
        """

        self.fault_rate = str(self.ui_int.fault_rate_slider.value() + 1)
        self.ui_int.fault_rate_textbrowser.setPlainText(self.fault_rate)

        return self.fault_rate

    def fault_imp_rate_slider(self):
        """
        It is the function that allows setting the Fault Implementation Rate value.
        This function allows you to determine what percentage of images in the normal
        image folder will have fault injected. When the slider there is scrolled,
        the desired rate value is displayed in the box. Box overwriting is not allowed
        (this feature can be added later, but the slider must be edited to react accordingly.)
        """

        self.fault_imp_rate = str(self.ui_int.fault_imp_rate_slider.value() + 1)
        self.ui_int.fault_imp_rate_textbrowser.setPlainText(self.fault_imp_rate)
        self.randomized_option_enabler(self.fault_imp_rate)

        return self.fault_imp_rate

    def details_fi_list_func(self):
        """
        It is the function where the Update FIP List button is defined.
        When a plan in the FI Plans list is selected, the content of the plan can
        be viewed in the Info section with this button.
        """

        try:
            self.ui_int.info_text.clear()
            self.fi_plan = self.ui_int.fi_plan_tree.selectedIndexes()[0].data()
            with open(
                str(ext.get_current_workspace()) + "/fi_plans/" + self.fi_plan,
                "r",
                encoding="utf-8",
            ) as fi_plan_file:
                self.ui_int.info_text.setText(fi_plan_file.read())
        except IndexError:
            self.pop_up_message(
                'Please choose one fault injection plan from "FI Plans"!'
            )
            ext.error_log_creator(IndexError)

    def read_fi_plans(self, plan_text):
        """
        It is the function that allows the FI plans to be read.
        """
        self.fi_plan = plan_text.text()
        return self.fi_plan

    def robot_camera_live(self, robot_camera):  # publish_camera will be added.
        """
        In real-time fault injection, it is the function of the button that enables the
        broadcasting camera to be opened via another terminal.
        """

        # It is checked whether ROS Camera is selected in the interface.
        ros_cam = self.ui_int.robot_camera_combobox.currentText()

        # If the user presses the key without entering any topic name in the
        # ros_cam_topic_text tab, they will receive this warning.
        ros_cam_topic_name = self.ui_int.ros_cam_topic_text.toPlainText()

        if ros_cam_topic_name == "Enter here ROS Camera Topic name ":
            self.pop_up_message(
                "Please enter ROS Camera topic name into the "
                + '"ROS Cam. Topic" section!'
            )
        else:
            if ros_cam == "ROS Camera":
                # publish_camera can also be selected. robot_camera represents
                # the topic of the published camera, and publish_camera is
                # another desired topic name.
                robot_camera = self.ui_int.ros_cam_topic_text.toPlainText()
                os.system(
                    "gnome-terminal -x rosrun image_view image_view image:="
                    + robot_camera
                )
            else:
                self.pop_up_message("ROS Camera connection failed.")

    def default_robot_camera_configs(self):
        """
        It is the function that regulates the interface formats of the configuration
        settings opened when Robot Camera is active.
        """
        self.ui_int.ros_cam_topic_text.setFontItalic(True)
        self.ui_int.ros_cam_fi_freq_text.setFontItalic(True)
        self.ui_int.ros_cam_topic_text.setFontPointSize(9.0)
        self.ui_int.ros_cam_fi_freq_text.setFontPointSize(9.0)

    def update_ros_cam_topic_config(self):
        """
        It is the function that updates the fonts and font size when changes are
        made in the ROS Camera configuration.
        """
        self.ui_int.ros_cam_topic_text.setFontItalic(False)
        self.ui_int.ros_cam_topic_text.setFontPointSize(11.0)

    def update_ros_cam_fi_freq_config(self):
        """
        It is the function that updates the fonts and font size when changes
        are made in the ROS Stream Frequency configuration.
        """
        self.ui_int.ros_cam_fi_freq_text.setFontItalic(False)
        self.ui_int.ros_cam_fi_freq_text.setFontPointSize(11.0)

    def faulty_image_list_saver(self, fi_image_folder, fi_image_list):
        date_info = datetime.datetime.now()
        curr_time = (
            str(date_info.day)
            + str(date_info.hour)
            + str(date_info.minute)
            + str(date_info.second)
        )

        if not os.path.exists("fi_image_list_logs"):
            os.mkdir("fi_image_list_logs")
        fi_logfile_name = "fi_image_list_" + str(curr_time) + ".txt"
        with open(
            "fi_image_list_logs/" + str(fi_logfile_name), "a", encoding="utf-8"
        ) as fi_list_file:
            fi_list_file.write("Created: " + str(date_info))
            fi_list_file.write("\nFault Value: ")
            total_normal_image = len(self.normal_image_list)
            fault_imp_value = len(fi_image_list)
            fi_list_file.write(str(fault_imp_value) + "/" + str(total_normal_image))
            fi_list_file.write("\nFaulty Image Name List: \n")
            fi_list_file.write(str(fi_image_list))
            fi_list_file.write("\nRemain Normal Image Name List: \n")
            remain_norm_img_list = ext.list_substractor(
                self.normal_image_list, fi_image_list
            )
            fi_list_file.write(str(remain_norm_img_list))
        # Saving last fi logfile and fi image folder name for multipartial fi process
        self.last_fi_image_list = fi_image_list
        self.last_fi_image_folder = fi_image_folder
        self.last_fi_logname = fi_logfile_name

        return self.last_fi_image_list, self.last_fi_image_folder, self.last_fi_logname

    def check_last_fi_process(self):
        print("--checking")
        if (
            self.last_fi_image_list is not None
            and self.last_fi_image_folder == self.fi_image_folder
        ):
            # Hata enjekte edilmemiş resimlerin geçici bir normal klasöre taşınması,
            # bu klasörün normal resim klasörü olarak
            # işleme dahil edilmesi gerekiyor.
            self.repeated_fi_process = True
        else:
            print("--not repeated")
            self.repeated_fi_process = False
            self.repeated_process_lock = False

        return self.repeated_fi_process

    def repeated_fi(self):
        """Tekrarli hata enj durumunda yeni normal img ve fi img sayisinin hesaplandigi fonk."""
        # önceden uygulanmis hatali resimlerin, normal resim listesinden
        # cikarildiktan sonra kalan normal resimlerin sayisi
        a_file = open("fi_image_list_logs/" + self.last_fi_logname)

        fi_image_list_line = [3]
        normal_image_list_line = [5]
        fi_image_list = []
        norm_image_list = []

        for position, line in enumerate(a_file):
            # fi img listesini cikarir
            if position in fi_image_list_line:
                fi_image_list = line
            # geriye kalan normal img listesini cikarir
            elif position in normal_image_list_line:
                norm_image_list = line

        return len(norm_image_list), len(fi_image_list)

    def randomized_option_enabler(self, fault_imp_rate):
        """When partial fault injection is active, randomized option is locked"""
        if fault_imp_rate != 100:
            self.ui_int.randomize_check.setEnabled(False)
        else:
            self.ui_int.randomize_check.setEnabled(True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
