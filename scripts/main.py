#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CamFITool ROS Edition (v1.2.2)
"""

import sys
import os
import datetime
import time

from PyQt5 import QtWidgets

import ui_interface as Ui
#import qt_core as Qt

from offline_fault_injector_ui import main as ofi
from realtime_fault_injector_ui import RealtimeFaultInjector as rfi

class MainWindow(QtWidgets.QMainWindow):
    """
    CamFITool Interface MainWindow Class
    """
    def __init__(self):
        # Değişkenler
        self.normal_image_file = None
        self.fi_image_file = None
        self.fi_freq = None
        self.fi_plan = None
        self.fi_type = None
        self.fault_type = None
        self.fault_rate = None
        self.robot_camera_type = None
        self.camera_type = None
        self.ros_cam_topic = None
        self.ros_cam_fi_freq = None
        self.robot_camera = None
        self.publish_camera = "/camfitool_cam/faulty_image_raw"

        QtWidgets.QMainWindow.__init__(self)
        self.ui_int = Ui.Ui_MainWindow()
        self.ui_int.setupUi(self)
        self.show()

        self.setWindowIcon(Ui.QtGui.QIcon(":icons/imfit_logo.png"))
        self.setWindowTitle("Camera Fault Injection Tool")

        QtWidgets.QSizeGrip(self.ui_int.size_grip)

        self.ui_int.camera_type_combobox.addItems(['--Select one--','TOF','RGB'])
        self.ui_int.fi_type_combobox.addItems(['--Select one--','Offline','Real-time'])

        self.ui_int.fi_type_combobox.currentTextChanged.connect(self.real_time_options)
        self.ui_int.robot_camera_combobox.currentTextChanged.connect(self.ros_camera_options)
        self.ui_int.camera_type_combobox.currentTextChanged.connect(self.camera_type_options)

        self.ui_int.fault_rate_textbrowser.setPlainText("-")
        self.ui_int.fault_rate_slider.valueChanged.connect(self.fault_rate_slider)

        self.ui_int.find_image_file_button.clicked.connect(self.find_image_file)
        self.ui_int.find_fi_file_button.clicked.connect(self.find_fi_image_file)
        self.ui_int.apply_fault_button.clicked.connect(self.apply_fault)
        self.ui_int.save_fi_plan_button.clicked.connect(self.save_fi_plan)
        self.ui_int.help_button.clicked.connect(self.help_section)
        self.ui_int.about_button.clicked.connect(self.about_section)
        self.ui_int.show_fi_plan_details_button.clicked.connect(self.details_fi_list_func)
        self.ui_int.progressBar.setValue(0)

        # Robot Camera butonuna basıldığında, robot_camera değişkenindeki ros düğümü
        # izlemeye alınır.
        self.ui_int.robot_camera_button.clicked.connect(lambda:
            self.robot_camera_live(self.robot_camera))

        # Arayüz açıldığında default normal ve hatalı resim klasörleri ile fi plan
        # listesi otomatik olarak yüklenir.
        self.starter_folder_indexes()

        # ROS Cam Text ve ROS Stream Freq sekmelerinin yazı tiplerinin ve boyutlarının
        # ayarlandığı kısım
        self.default_robot_camera_configs()

        self.ui_int.info_text.setText("Welcome to Camera Fault Injection Tool ROS Edition v1.2.3")
        self.show()

    def starter_folder_indexes(self):
        """
        Normal ve hatalı resim klasörlerinin modül isimleri ve standart konumlarının,
        "folder_module" ve "folder_location" değişkenleri olarak tanımlandığı
        fonksiyondur.
        """
        folder_list = [["image_file", str(self.get_current_workspace())+\
        '/images/normal_image_folders/'],["fi_file", str(self.get_current_workspace())+\
        '/images/fault_image_folders/']]

        for i,j in folder_list:
            self.open_default_folders(i,j)

        self.update_fi_list_func()

    def open_default_folders(self, folder_module, folder_location):

        """
        starter_folder_indexes fonksiyonundan gelen modül ve konum bilgilerine uygun
        olarak default klasörleri arayüze getiren fonksiyondur.
        """
        model = QtWidgets.QFileSystemModel()
        model.setRootPath(folder_location)

        if folder_module == "fi_file":
            self.ui_int.fi_file_tree.setModel(model)
            self.ui_int.fi_file_tree.setRootIndex(model.index(folder_location))
            self.ui_int.fi_file_tree.setSortingEnabled(True)
            self.ui_int.fi_file_tree.hideColumn(1)
            self.ui_int.fi_file_tree.hideColumn(2)
            self.ui_int.fi_file_tree.setColumnWidth(0,200)
        else:
            self.ui_int.image_file_tree.setModel(model)
            self.ui_int.image_file_tree.setRootIndex(model.index(folder_location))
            self.ui_int.image_file_tree.setSortingEnabled(True)
            self.ui_int.image_file_tree.hideColumn(1)
            self.ui_int.image_file_tree.hideColumn(2)
            self.ui_int.image_file_tree.setColumnWidth(0,200)

    def find_image_file(self):
        """
        Hata uygulanacak olan normal resimlerin bulunduğu klasörün seçildiği
        fonksiyondur.
        """

        self.normal_image_file = str(QtWidgets.QFileDialog.getExistingDirectory(self,\
            "Select Normal Images Directory", str(self.get_current_workspace())+\
            'images/normal_image_folders/'))

        model = QtWidgets.QFileSystemModel()
        model.setRootPath(self.normal_image_file)

        self.ui_int.image_file_tree.setModel(model)
        self.ui_int.image_file_tree.setRootIndex(model.index(self.normal_image_file))
        self.ui_int.image_file_tree.setSortingEnabled(True)
        self.ui_int.image_file_tree.hideColumn(1)
        self.ui_int.image_file_tree.hideColumn(2)
        self.ui_int.image_file_tree.setColumnWidth(0,200)


    def find_fi_image_file(self):
        """
        Hata uygulanan resimlerin kaydedileceği klasörün seçildiği fonksiyondur.
        """

        self.fi_image_file = str(QtWidgets.QFileDialog.getExistingDirectory(self,\
            "Select Faulty Images Directory", str(self.get_current_workspace())+\
            'images/fault_image_folders/'))

        model = QtWidgets.QFileSystemModel()
        model.setRootPath(self.fi_image_file)

        self.ui_int.fi_file_tree.setModel(model)
        self.ui_int.fi_file_tree.setRootIndex(model.index(self.fi_image_file))
        self.ui_int.fi_file_tree.setSortingEnabled(True)
        self.ui_int.fi_file_tree.hideColumn(1)
        self.ui_int.fi_file_tree.hideColumn(2)
        self.ui_int.fi_file_tree.setColumnWidth(0,200)

    def update_fi_list_func(self):
        """
        Update FIP List butonunun tanımlandığı fonksiyondur. Yeni fi planlar
        kaydedildiğinde doğrudan FI Plans kısmına düşmez. Her yeni kayıttan
        sonra oradaki listeyi bu butonla güncellemek mümkündür.
        """
        onlyfiles_location = str(self.get_current_workspace())+'/fi_plans'

        model = QtWidgets.QFileSystemModel()
        model.setRootPath(onlyfiles_location)

        self.ui_int.fi_plan_tree.setModel(model)
        self.ui_int.fi_plan_tree.setRootIndex(model.index(onlyfiles_location))
        self.ui_int.fi_plan_tree.setSortingEnabled(True)
        self.ui_int.fi_plan_tree.hideColumn(1)
        self.ui_int.fi_plan_tree.hideColumn(2)
        self.ui_int.fi_plan_tree.setColumnWidth(0,200)


    def real_time_options(self):
        """
        Fault Injection Type menusünün ayarlandığı fonksiyondur. Real-time
        seçildiğinde, robotun kamera çeşitleri (Robot Camera seçeneği)
        seçilebilir hale gelir.

        """

        if self.ui_int.fi_type_combobox.currentText() == "Real-time":
            self.ui_int.robot_camera_combobox.clear()
            self.ui_int.robot_camera_combobox.addItems(['--Select one--','ROS Camera'])
            #self.ui_int.randomize_check.setText("CV2 Screen")
            self.ui_int.randomize_check.setEnabled(False)

            # TOF Realtime özelliği eklenince silinecek
            self.ui_int.camera_type_combobox.clear()
            self.ui_int.camera_type_combobox.addItems(['--Select one--',
                'TOF (Under-development)','RGB'])

        elif self.ui_int.fi_type_combobox.currentText() == "Offline":
            self.ui_int.robot_camera_combobox.clear()
            self.ui_int.robot_camera_combobox.addItems(['None'])
            #self.ui_int.randomize_check.setText("Randomize")
            self.ui_int.randomize_check.setEnabled(True)

            # TOF Realtime özelliği eklenince silinecek
            self.ui_int.camera_type_combobox.clear()
            self.ui_int.camera_type_combobox.addItems(['--Select one--','TOF','RGB'])

        else:
            self.ui_int.robot_camera_combobox.clear()
            self.ui_int.robot_camera_combobox.addItems(['None'])

    def ros_camera_options(self):
        """
        Robot Camera  menusünün ayarlandığı fonksiyondur. ROS Camera seçildiğinde,
        kullanıcıdan realtime hata uygulanması istenen ROS kamera topiğinin
        ismini girebileceği bir text bar aktif hale gelecektir. None seçildiğinde
        ise bu kısım kaybolur.
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
            self.ui_int.ros_cam_fi_freq_text.setText("Enter here ROS Stream Frequency value")
            self.robot_camera = self.ui_int.ros_cam_topic_text.toPlainText()
            self.fi_freq = self.ui_int.ros_cam_fi_freq_text.toPlainText()

            # Robot Camera konfigürasyonlarında düzenleme yapıldığında fontları ve
            # yazı boyutunu düzenler.
            self.ui_int.ros_cam_topic_text.textChanged.connect(self.update_ros_cam_topic_config)
            self.ui_int.ros_cam_fi_freq_text.textChanged.connect(self.update_ros_cam_fi_freq_config)

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



    def camera_type_options(self):
        """
        Camera Type menusünün ayarlandığı fonksiyondur. Camera tipi RGB ya da
        TOF seçildiğinde ona göre Fault Type menusünü düzenler.
        """

        if self.ui_int.camera_type_combobox.currentText() == "RGB":
            self.ui_int.fault_type_combobox.clear()
            self.ui_int.fault_type_combobox.addItems(['--Select one--','Open',\
                'Close','Erosion','Dilation','Gradient','Motion-blur',\
                'Partialloss (Under-development)'])
        elif self.ui_int.camera_type_combobox.currentText() == "TOF":
            self.ui_int.fault_type_combobox.clear()
            self.ui_int.fault_type_combobox.addItems(['--Select one--','Salt&Pepper',
                'Gaussian','Poisson'])
        else:
            self.ui_int.fault_type_combobox.clear()
            self.ui_int.fault_type_combobox.addItems(['None'])

    def apply_fault(self):
        """
        Apply Fault butonunun çalıştırıldığı fonksiyondur. Camera Fault
        Configuration kısmında seçilen özelliklere uygun hatanın, Normal
        Image Folders kısmında seçilen klasördeki resimlere uygulanıp, FI
        Image Folder kısmında seçilen klasöre bu hatalı resimlerin
        kaydı işlemini başlatır.
        """
        #### OFFLINE FAULT INJECTION PART ####
        if self.ui_int.fi_type_combobox.currentText() == "Offline":
            print("Processing..")
            # Hata uygulama işlemi başladığında Apply Fault butonu çalışmaz
            # hale getirilir. Hata işlemi tamamlandıktan sonra buton yeniden
            # çalışır hale döndürülür.

            self.ui_int.apply_fault_button.setEnabled(False)
            self.ui_int.apply_fault_button.setStyleSheet("background-color: rgb(255, 255, 255);"
                                                        "color: rgb(0, 0, 0);")
            self.ui_int.apply_fault_button.setText("Processing")
            self.ui_int.apply_fault_button.setIcon(Ui.QtGui.QIcon(":icons/cil-external-link.png"))

            # Kaydedilen plan listesinden plan seçilip uygulama eklendiğinde
            # bu satır kaldırılacak.
            plan_from_list = False
            if plan_from_list:
                try:
                    self.ui_int.info_text.clear()
                    with open(str(self.get_current_workspace())+'/fi_plans/'+\
                        self.fi_plan, "r", encoding="utf-8") as fi_plan_file:
                        self.ui_int.info_text.setText("FI Plan Applying ...\n-----------------\n"+\
                            fi_plan_file.read())
                except IndexError:
                    self.pop_up_message('Please choose one fault injection plan from "FI Plans"!')
                    self.error_log(IndexError)
                else:
                    if self.ui_int.randomize_check.isChecked():
                        print("randomized")
                    else:
                        print("unrandomized")
            else:
                #### APPLY FAULT SECTION ############
                self.info_temp()
                file_path = self.get_current_workspace()
                ## Normal ve Hatalı resimler tablosunda tıklanmış olan klasör işleme konur.
                # Adresler değişmeli, seçtiğimiz klasörün konumu otomatik gelmeli.
                try:
                    normal_image_file = str(file_path)+"/images/normal_image_folders/"+\
                        str(self.ui_int.image_file_tree.selectedIndexes()[0].data())+"/"
                    fi_image_file = str(file_path)+"/images/fault_image_folders/"+\
                        str(self.ui_int.fi_file_tree.selectedIndexes()[0].data())+"/"
                    randomized = self.ui_int.randomize_check.isChecked()
                    resource, count, fi_image_name_list = ofi(normal_image_file, fi_image_file,
                        self.camera_type, self.fault_type, self.fault_rate, randomized)

                    ###################################
                    # Randomize seçeneği aktifken, sistem rastgele sayıda hatalı resim oluşturur.
                    # Hata basılan resimler rastgele seçilir.

                    if randomized:
                        self.progress_counter(count)
                        self.ui_int.info_text.setPlainText(resource+\
                            str("\nFault Injected Files:\n")+\
                            str(fi_image_name_list))

                    else:
                        self.progress_counter(count)
                        self.ui_int.info_text.setPlainText(resource)
                except IndexError:
                    self.pop_up_message("Please choose one Normal and one "+\
                        "Fault image folders from Folder Selection Section on the left side.")
                    self.error_log(IndexError)
                except Exception as error_msg:
                    self.pop_up_message("Something wrong! You should look logs file for details.")
                    self.error_log(error_msg)

            print("Completed..")

            # Fault uygulama tamamlandığında, Apply Fault butonu eski haline getirilir.
            self.ui_int.apply_fault_button.setDisabled(False)
            self.ui_int.apply_fault_button.setStyleSheet("background-color: rgb(6, 37, 98);"
                                                        "color: rgb(255, 255, 255);")
            self.ui_int.apply_fault_button.setText("Apply Fault")
            self.ui_int.apply_fault_button.setIcon(Ui.QtGui.QIcon(":icons/cil-cloud-upload.png"))

        #### REALTIME FAULT INJECTION PART ####
        elif self.ui_int.fi_type_combobox.currentText() == "Real-time":
            print("Processing..")
            self.ui_int.info_text.setText("Fault injecting to the ROS camera stream...")
            self.robot_camera = self.ui_int.ros_cam_topic_text.toPlainText()
            self.pop_up_message("This process will be broken this interface. "+\
             "This will be fixed.")

            # Kaydedilen plan listesinden plan seçilip uygulama eklendiğinde bu satır kaldırılacak.
            plan_from_list = False

            if plan_from_list:
                try:
                    self.ui_int.info_text.clear()
                    with open(str(self.get_current_workspace())+'/fi_plans/'+\
                        self.fi_plan, "r", encoding="utf-8") as fi_plan_file:
                        self.ui_int.info_text.setText("FI Plan Applying ...\n-----------------\n"+\
                            fi_plan_file.read())
                except IndexError:
                    self.pop_up_message('Please choose one fault injection plan from "FI Plans"!')
                    self.error_log(IndexError)
            else:
                self.info_temp()
                cv2_screen = False # default

                ## Randomized fonksiyonu, realtime modunda CV2 Screen moduna dönüşür.
                # Kullanıcı isterse hata yayınını CV2 panelinden ayrıca görüntüleyebilir.
                # Bu kısım henüz test aşamasındadır.

                #if self.ui_int.randomize_check.isChecked():
                #    cv2_screen is True
                #else:
                #    cv2_screen is False

                self.publish_camera = self.robot_camera ## Değişecek.

                try:
                    # Eğer kullanıcı int bir değer yerine str girişi yaparsa sistem
                    # hata mesajı verir, apply_fault çalışmaz.
                    self.fi_freq = int(self.ui_int.ros_cam_fi_freq_text.toPlainText())
                except ValueError:
                    self.pop_up_message("Please enter a valid frequency value!")
                    self.error_log(ValueError)
                else:
                    rfi(self.robot_camera, self.publish_camera, self.camera_type,\
                        self.fault_type, self.fault_rate, self.fi_freq, cv2_screen)


        else:
            self.pop_up_message("Something is wrong! You should check your fault configuration.")
            self.error_log("Fault configuration error! It may be missing or created "+\
                "incorrectly. Fill in all the configurations and try again.")

    def progress_counter(self, count):
        """
        Progress barını kontrol eden fonksiyondur.
        """
        self.ui_int.progressBar.setFormat(" ")
        for i in range(count):
            counter = (i/count)*100 + 1
            self.ui_int.progressBar.setValue(int(counter))
            time.sleep(count/10000)
        self.ui_int.progressBar.setFormat("Completed")

    def camera_fault_config(self):
        """
        Camera Fault Configuration menusünde tanımlanan özellikleri kaydeden fonksiyondur.
        """

        self.robot_camera_type = self.ui_int.robot_camera_combobox.currentText()
        self.camera_type = self.ui_int.camera_type_combobox.currentText()
        self.fi_type = self.ui_int.fi_type_combobox.currentText()
        self.fault_type = self.ui_int.fault_type_combobox.currentText()

    def info_temp(self):
        # Bu kısım düzenlenebilir.
        """
        Camera Fault Configuration menusüsünde tanımlanan özellikleri Info bölümüne
        yazan fonksiyondur. Bunun için configleri temp.txt adlı geçici bir dosyaya
        kaydeder, o dosyadan revize edilen info bilgisini Info sekmesine yazıp temp
        dosyasını siler.
        """
        try:
            self.robot_camera_type = self.ui_int.robot_camera_combobox.currentText()
            self.camera_type = self.ui_int.camera_type_combobox.currentText()
            self.fi_type = self.ui_int.fi_type_combobox.currentText()
            self.fault_type = self.ui_int.fault_type_combobox.currentText()

            if self.fi_type == "Offline":
                with open("temp.txt", "a", encoding="utf-8") as temp_file:
                    temp_file.write("Robot Camera: ")
                    temp_file.write(self.robot_camera_type)
                    temp_file.write("\nCamera Type: ")
                    temp_file.write(self.camera_type)
                    temp_file.write("\nFault Inj. Type: ")
                    temp_file.write(self.fi_type)
                    temp_file.write("\nFault Type: ")
                    temp_file.write(self.fault_type)
                    temp_file.write("\nFault Rate: ")
                    temp_file.write(self.fault_rate)
                    temp_file.write("%")
            else:
                self.ros_cam_topic = self.ui_int.ros_cam_topic_text.toPlainText()
                self.ros_cam_fi_freq = self.ui_int.ros_cam_fi_freq_text.toPlainText()

                with open("temp.txt", "a", encoding="utf-8") as temp_file:
                    temp_file.write("Robot Camera: ")
                    temp_file.write(self.robot_camera_type)
                    temp_file.write("\nROS Camera Topic: ")
                    temp_file.write(self.ros_cam_topic)
                    temp_file.write("\nROS Camera FI Stream Freq: ")
                    temp_file.write(self.ros_cam_fi_freq)
                    temp_file.write("Hz")
                    temp_file.write("\nCamera Type: ")
                    temp_file.write(self.camera_type)
                    temp_file.write("\nFault Inj. Type: ")
                    temp_file.write(self.fi_type)
                    temp_file.write("\nFault Type: ")
                    temp_file.write(self.fault_type)
                    temp_file.write("\nFault Rate: ")
                    temp_file.write(self.fault_rate)
                    temp_file.write("%")

        except AttributeError:
            self.pop_up_message("Fault Rate Missing!")
            self.error_log(AttributeError)

        except TypeError:
            self.pop_up_message("Fault Rate Missing!")
            self.error_log(TypeError)

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
            #else:
            #    if self.ui_int.randomize_check.isChecked() == True:
            #        f.write("\nCV2 Screen: True")
            #    elif self.ui_int.randomize_check.isChecked() == False:
            #        f.write("\nCV2 Screen: False")
            #    else:
            #        pass

            temp_file.close()
            with open("temp.txt", "r", encoding="utf-8") as temp_file:
                self.ui_int.info_text.setText(temp_file.read())
            os.remove("temp.txt")

    def save_fi_plan(self):
        """
        Save FI Plan butonunun tanımlandığı fonksiyondur. Camera Fault Config
        menusünde tanımlanan hata özelliklerini seçilen bir .txt dosyasına
        kaydeder. Bu kayıt işlemi sonrası onay mesajını Info sekmesinde yayınlar.
        (Bu kısımda yapılan kayıt sistemi daha sonra .json uzantılı olacak şekilde
        düzenlenecektir.)
        """
        self.info_temp()

        try:
            # S_File will get the directory path and extension.
            save_file = Ui.QtWidgets.QFileDialog.getSaveFileName(None,'Save FI Plan',\
                str(self.get_current_workspace())+'/fi_plans/fi_plan', "Text Files (*.txt)")

            # This will let you access the test in your QTextEdit
            save_text = self.ui_int.info_text.toPlainText()

            #self.fi_plan(Text)

            # This will prevent you from an error if pressed cancel on file dialog.
            if save_file[0]:
                # Finally this will Save your file to the path selected.
                with open(save_file[0], 'w', encoding="utf-8") as temp_file:
                    date = datetime.datetime.now()
                    temp_file.write("Created: "+str(date.ctime()))
                    temp_file.write("\n----------------------------------\n")
                    temp_file.write(save_text)

            self.ui_int.info_text.setText("FI Plan Saved! For Details any Plan, "+\
             "Please Choose One of Them from 'FI Plans' Section and click "+\
              "'Show FIP Details' button!")

        except AttributeError:
            self.pop_up_message("Fault Rate Missing!")
            self.error_log(AttributeError)

        self.update_fi_list_func()

    @classmethod
    def pop_up_message(cls, msg):
        """
        Demo Tooldaki hata mesajlarını pop up olarak yayınlayan fonksiyondur.
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
        About butonunun tanımlandığı fonksiyondur.
        """
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setText("Camera Fault Injector Tool, Oct 2021\n"+\
            "For More Information, Contact kerem.erdogmus@inovasyonmuhendislik.com.")
        msg_box.setWindowTitle("About")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec()

    @classmethod
    def help_section(cls):
        """
        Help butonunun tanımlandığı fonksiyondur.
        """
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setInformativeText("Welcome to Camera Fault Injector Tool v1.2.2\n\n")
        msg_box.setDetailedText("""Using this tool you can:
        - You can apply the faults you choose in the configuration menu to the images in the
        image library you want, and save these wrong images to the folder you want.
        - You can apply these faults to all images as well as to a random number of images,
        creating a mixed library of faulty images without touching the remaining images
        (only offline fault application).
        - You can save the configuration of the fault you have applied, and view the fault
        plans you have saved as you wish.
        - You can specify the rate of fault to be applied.
        - For now, three different fault types can be applied offline to images
        (with .bmp extension) obtained from TOF camera.
        - For now, six different fault types can be applied offline to images (with .jpg or
        .png extension) and real-time stream obtained from RGB camera.
        - You can watch ROS Camera streams.
        - You can specify the rate of real-time fault injecting frequency to be applied.
        """)
        msg_box.setWindowTitle("Help")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec()


    def fault_rate_slider(self):
        """
        Camera Fault Configuration menusündeki Fault Rate değerinin ayarlanmasını
        sağlayan fonksiyondur. Oradaki slider kaydırıldığında istenen rate değeri
        kutuda görüntülenir. Kutu üzerine yazmaya izin verilmez (bu özellik daha
        sonra eklenebilir ancak slider da buna göre tepki verecek şekilde
        düzenlenmelidir.)
        """

        self.fault_rate = str(self.ui_int.fault_rate_slider.value()+1)
        self.ui_int.fault_rate_textbrowser.setPlainText(self.fault_rate)

        return self.fault_rate

    def details_fi_list_func(self):
        """
        Update FIP List butonunun tanımlandığı fonksiyondur. FI Plans listesinde
        yer alan bir plan seçildiğinde bu butonla ilgili planın içeriği Info
        kısmında görüntülenebilir.
        """

        try:
            self.ui_int.info_text.clear()
            self.fi_plan = self.ui_int.fi_plan_tree.selectedIndexes()[0].data()
            with open(str(self.get_current_workspace())+'/fi_plans/'+\
                self.fi_plan, "r", encoding="utf-8") as fi_plan_file:
                self.ui_int.info_text.setText(fi_plan_file.read())
        except IndexError:
            self.pop_up_message('Please choose one fault injection plan from "FI Plans"!')
            self.error_log(IndexError)

    def read_fi_plans(self, plan_text):
        """
        FI Planların okunmasını sağlayan fonksiyondur.
        """
        self.fi_plan = plan_text.text()
        print(self.fi_plan)
        return self.fi_plan

    def robot_camera_live(self, robot_camera): # publish_camera ileride eklenecek.
        """
        Real-time hata enjeksiyonunda, yayın yapan kameranın bir başka terminal
        aracılığıyla açılmasını sağlayan butonun fonksiyonudur.
        """

        # Arayüzde ROS Camera seçili olup olmadığı kontrol edilir.
        ros_cam = self.ui_int.robot_camera_combobox.currentText()

        # Kullanıcı ros_cam_topic_text sekmesine herhangi bir topic ismi girmeden
        # tuşa basarsa bu uyarıyı alır.
        ros_cam_topic_name = self.ui_int.ros_cam_topic_text.toPlainText()

        if ros_cam_topic_name == "Enter here ROS Camera Topic name ":
            self.pop_up_message('Please enter ROS Camera topic name into the '+\
                '"ROS Cam. Topic" section!')
        else:
            if ros_cam == "ROS Camera":
                # publish_camera da seçilebilir. robot_camera, yayınlanan kameranın
                # topiğini temsil eder, publish_camera ise istenen bir başka
                # topic ismidir.
                robot_camera = self.ui_int.ros_cam_topic_text.toPlainText()
                os.system("gnome-terminal -x rosrun image_view image_view image:="+robot_camera)
            else:
                self.pop_up_message('ROS Camera connection failed.')

    def default_robot_camera_configs(self):
        """
        Robot Camera aktifken açılan konfigürasyon ayarlamalarının arayüz biçimlerini
        düzenleyen fonksiyondur.
        """
        self.ui_int.ros_cam_topic_text.setFontItalic(True)
        self.ui_int.ros_cam_fi_freq_text.setFontItalic(True)
        self.ui_int.ros_cam_topic_text.setFontPointSize(9.0)
        self.ui_int.ros_cam_fi_freq_text.setFontPointSize(9.0)

    def update_ros_cam_topic_config(self):
        """
        ROS Camera konfigürasyonunda değişiklik yapıldığında fontları ve yazı boyutunu
        güncelleyen fonksiyondur.
        """
        self.ui_int.ros_cam_topic_text.setFontItalic(False)
        self.ui_int.ros_cam_topic_text.setFontPointSize(11.0)

    def update_ros_cam_fi_freq_config(self):
        """
        ROS Stream Frequency konfigürasyonunda değişiklik yapıldığında fontları ve
        yazı boyutunu güncelleyen fonksiyondur.
        """
        self.ui_int.ros_cam_fi_freq_text.setFontItalic(False)
        self.ui_int.ros_cam_fi_freq_text.setFontPointSize(11.0)

    @classmethod
    def error_log(cls,msg):
        """
        Arayüz hata mesajı verdiğinde, hata detaylarının kaydının tutulmasını sağlayan
        fonksiyondur.
        """

        try:
            os.makedirs("logs")
        except OSError:
            pass

        curr_date = datetime.datetime.now()
        with open("logs/error_log_"+str(curr_date.hour)+str(curr_date.minute)+\
            str(curr_date.second)+".txt", "w", encoding="utf-8") as error_log:
            error_log.write(f"ERROR: {curr_date.ctime()}:\n---\n {msg}\n")

    @classmethod
    def get_current_workspace(cls):
        """
        Tool'un çalıştığı workspace konumunu veren fonksiyondur.
        """
        file_full_path = os.path.dirname(os.path.realpath(__file__))

        # CamFITool'un yüklü olduğu çalışma ortamının konumunu alır.
        camfitool_ws_location = file_full_path.split('/', 10)
        camfitool_ws_location = '/'+camfitool_ws_location[1]+'/'+ camfitool_ws_location[2]+'/'+\
             camfitool_ws_location[3]+'/'+ camfitool_ws_location[4]+'/'+camfitool_ws_location[5]
        return camfitool_ws_location


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
