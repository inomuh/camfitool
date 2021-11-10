import sys
import os
import datetime
import time

from os import listdir
from os.path import isfile, join
from typing import Tuple

from ui_interface import *
from qt_core import *

from offline_fault_injector_ui import main as ofi
from realtime_fault_injector_ui import RealtimeFaultInjector as rfi


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
                                                      
        self.setWindowIcon(QtGui.QIcon(":icons/imfit_logo.png"))
        self.setWindowTitle("Camera Fault Injector Demo Tool")

        QSizeGrip(self.ui.size_grip)

        self.ui.camera_type_combobox.addItems(['--Select one--','TOF','RGB'])
        self.ui.fi_type_combobox.addItems(['--Select one--','Offline','Real-time'])

        self.ui.fi_type_combobox.currentTextChanged.connect(self.real_time_options)
        self.ui.robot_camera_combobox.currentTextChanged.connect(self.ros_camera_options)
        self.ui.camera_type_combobox.currentTextChanged.connect(self.camera_type_options)

        self.ui.fault_rate_textbrowser.setPlainText("-")
        self.ui.fault_rate_slider.valueChanged.connect(lambda: self.fault_rate_slider())

        self.ui.find_image_file_button.clicked.connect(lambda: self.find_image_file())
        self.ui.find_fi_file_button.clicked.connect(lambda: self.find_fi_image_file())
        self.ui.apply_fault_button.clicked.connect(lambda: self.apply_fault())
        self.ui.save_fi_plan_button.clicked.connect(lambda: self.save_fi_plan())
        self.ui.help_button.clicked.connect(lambda: self.help_section())
        self.ui.about_button.clicked.connect(lambda: self.about_section())
        self.ui.show_fi_plan_details_button.clicked.connect(lambda: self.details_fi_list_func())
        self.ui.progressBar.setValue(0)
        
        # Robot Camera butonuna basıldığında, robot_camera değişkenindeki ros düğümü izlemeye alınır.
        self.robot_camera = "right_rokos/color_camera/image_raw"
        self.publish_camera = "right_rokos/color_camera/image_raw_faulty"
        self.ui.robot_camera_button.clicked.connect(lambda: self.robot_camera_live(self.robot_camera, self.publish_camera))
        
        # Arayüz açıldığında default normal ve hatalı resim klasörleri ile fi plan listesi otomatik olarak yüklenir.  
        self.starter_folder_indexes()
        
        # ROS Cam Text ve ROS Stream Freq sekmelerinin yazı tiplerinin ve boyutlarının ayarlandığı kısım
        self.default_robot_camera_configs()
        
        self.ui.info_text.setText("Welcome to Camera Fault Injector Demo Tool v1.2")
        self.show()

    def test(self):
        """
        Test fonksiyonu
        """
        print("test")
        pass

    def starter_folder_indexes(self):
        """
        Normal ve hatalı resim klasörlerinin modül isimleri ve standart konumlarının, "folder_module" ve "folder_location" değişkenleri olarak tanımlandığı
        fonksiyondur.
        """
        list = [["image_file", str(self.get_current_workspace())+'/images/normal_image_folders/'],["fi_file", str(self.get_current_workspace())+'/images/fault_image_folders/']]
        
        for i,j in list:
            self.open_default_folders(i,j)
        
        self.update_fi_list_func() 
    
    def open_default_folders(self, folder_module, folder_location):

        """
        starter_folder_indexes fonksiyonundan gelen modül ve konum bilgilerine uygun olarak default klasörleri
        arayüze getiren fonksiyondur.
        """
        model = QFileSystemModel()
        model.setRootPath(folder_location)

        if folder_module == "fi_file":
            self.ui.fi_file_tree.setModel(model)
            self.ui.fi_file_tree.setRootIndex(model.index(folder_location))
            self.ui.fi_file_tree.setSortingEnabled(True)
            self.ui.fi_file_tree.hideColumn(1)
            self.ui.fi_file_tree.hideColumn(2)
            self.ui.fi_file_tree.setColumnWidth(0,200)
        else:
            self.ui.image_file_tree.setModel(model)
            self.ui.image_file_tree.setRootIndex(model.index(folder_location))
            self.ui.image_file_tree.setSortingEnabled(True)
            self.ui.image_file_tree.hideColumn(1)
            self.ui.image_file_tree.hideColumn(2)
            self.ui.image_file_tree.setColumnWidth(0,200)
    
    def find_image_file(self):
        """
        Hata uygulanacak olan normal resimlerin bulunduğu klasörün seçildiği fonksiyondur.

        """

        self.normal_image_file = str(QFileDialog.getExistingDirectory(self, "Select Normal Images Directory", str(self.get_current_workspace())+'images/normal_image_folders/'))       
        
        model = QFileSystemModel()
        model.setRootPath(self.normal_image_file)

        self.ui.image_file_tree.setModel(model)
        self.ui.image_file_tree.setRootIndex(model.index(self.normal_image_file))
        self.ui.image_file_tree.setSortingEnabled(True)
        self.ui.image_file_tree.hideColumn(1)
        self.ui.image_file_tree.hideColumn(2)
        self.ui.image_file_tree.setColumnWidth(0,200)
        

    def find_fi_image_file(self):
        """
        Hata uygulanan resimlerin kaydedileceği klasörün seçildiği fonksiyondur.

        """
        
        self.fi_image_file = str(QFileDialog.getExistingDirectory(self, "Select Faulty Images Directory", str(self.get_current_workspace())+'images/fault_image_folders/'))       
        
        model = QFileSystemModel()
        model.setRootPath(self.fi_image_file)

        self.ui.fi_file_tree.setModel(model)
        self.ui.fi_file_tree.setRootIndex(model.index(self.fi_image_file))
        self.ui.fi_file_tree.setSortingEnabled(True)
        self.ui.fi_file_tree.hideColumn(1)
        self.ui.fi_file_tree.hideColumn(2)
        self.ui.fi_file_tree.setColumnWidth(0,200)

    def update_fi_list_func(self):
        """
        Update FIP List butonunun tanımlandığı fonksiyondur. Yeni fi planlar kaydedildiğinde doğrudan FI Plans kısmına düşmez.
        Her yeni kayıttan sonra oradaki listeyi bu butonla güncellemek mümkündür.
        """
        onlyfiles_location = str(self.get_current_workspace())+'/fi_plans'       
  
        model = QFileSystemModel()
        model.setRootPath(onlyfiles_location)

        self.ui.fi_plan_tree.setModel(model)
        self.ui.fi_plan_tree.setRootIndex(model.index(onlyfiles_location))
        self.ui.fi_plan_tree.setSortingEnabled(True)
        self.ui.fi_plan_tree.hideColumn(1)
        self.ui.fi_plan_tree.hideColumn(2)
        self.ui.fi_plan_tree.setColumnWidth(0,200)


    def real_time_options(self):
        """
        Fault Injection Type menusünün ayarlandığı fonksiyondur. Real-time seçildiğinde, robotun kamera çeşitleri (Robot Camera seçeneği) seçilebilir hale gelir.

        """
        
        if self.ui.fi_type_combobox.currentText() == "Real-time":
            self.ui.robot_camera_combobox.clear()
            self.ui.robot_camera_combobox.addItems(['--Select one--','ROS Camera'])
            #self.ui.randomize_check.setText("CV2 Screen")
            self.ui.randomize_check.setEnabled(False)

            # TOF Realtime özelliği eklenince silinecek
            self.ui.camera_type_combobox.clear()
            self.ui.camera_type_combobox.addItems(['--Select one--','TOF (Under-development)','RGB'])

        elif self.ui.fi_type_combobox.currentText() == "Offline":
            self.ui.robot_camera_combobox.clear()
            self.ui.robot_camera_combobox.addItems(['None'])
            #self.ui.randomize_check.setText("Randomize")
            self.ui.randomize_check.setEnabled(True)

            # TOF Realtime özelliği eklenince silinecek
            self.ui.camera_type_combobox.clear()
            self.ui.camera_type_combobox.addItems(['--Select one--','TOF','RGB'])

        else:
            self.ui.robot_camera_combobox.clear()
            self.ui.robot_camera_combobox.addItems(['None'])
    
    def ros_camera_options(self):
        """
        Robot Camera  menusünün ayarlandığı fonksiyondur. ROS Camera seçildiğinde, kullanıcıdan realtime hata uygulanması istenen ROS kamera topiğinin
        ismini girebileceği bir text bar aktif hale gelecektir. None seçildiğinde ise bu kısım kaybolur.

        """
        if self.ui.robot_camera_combobox.currentText() == "ROS Camera":

            self.ui.ros_cam_topic_label.setEnabled(True)
            self.ui.ros_cam_topic_text.setEnabled(True)
            self.ui.ros_cam_fi_freq_label.setEnabled(True)
            self.ui.ros_cam_fi_freq_text.setEnabled(True)
            self.ui.ros_cam_topic_text.setReadOnly(False)
            self.ui.ros_cam_fi_freq_text.setReadOnly(False)
            self.ui.ros_cam_topic_label.setText("ROS Cam. Topic  ")
            
            self.ui.ros_cam_topic_text.setText("Enter here ROS Camera Topic name ")
            self.ui.ros_cam_fi_freq_label.setText("Cam. Stream Freq (Hz)  ")
            self.ui.ros_cam_fi_freq_text.setText("Enter here ROS Stream Frequency value")
            self.robot_camera = self.ui.ros_cam_topic_text.toPlainText()
            self.fi_freq = self.ui.ros_cam_fi_freq_text.toPlainText()
            
            # Robot Camera konfigürasyonlarında düzenleme yapıldığında fontları ve yazı boyutunu düzenler.
            self.ui.ros_cam_topic_text.textChanged.connect(self.update_ros_cam_topic_config)
            self.ui.ros_cam_fi_freq_text.textChanged.connect(self.update_ros_cam_fi_freq_config)
        else:
            
            self.ui.ros_cam_topic_label.setEnabled(False)
            self.ui.ros_cam_topic_text.setEnabled(False)
            self.ui.ros_cam_fi_freq_label.setEnabled(False)
            self.ui.ros_cam_fi_freq_text.setEnabled(False)
            self.ui.ros_cam_topic_text.setReadOnly(True)
            self.ui.ros_cam_fi_freq_text.setReadOnly(True)
            self.ui.ros_cam_topic_label.setText(" ")
            self.ui.ros_cam_fi_freq_label.setText(" ")
            self.ui.ros_cam_topic_text.clear()
            self.ui.ros_cam_fi_freq_text.clear()
            self.default_robot_camera_configs()



    def camera_type_options(self):
        """
        Camera Type menusünün ayarlandığı fonksiyondur. Camera tipi RGB ya da TOF seçildiğinde ona göre Fault Type menusünü düzenler.
        """

        if self.ui.camera_type_combobox.currentText() == "RGB":
            self.ui.fault_type_combobox.clear()
            self.ui.fault_type_combobox.addItems(['--Select one--','Open','Close','Erosion','Dilation','Gradient','Motion-blur','Partialloss (Under-development)'])        
        elif self.ui.camera_type_combobox.currentText() == "TOF":
            self.ui.fault_type_combobox.clear()
            self.ui.fault_type_combobox.addItems(['--Select one--','Salt&Pepper','Gaussian','Poisson'])
        else:
            self.ui.fault_type_combobox.clear()
            self.ui.fault_type_combobox.addItems(['None'])
       
    def apply_fault(self):

        """
        Apply Fault butonunun çalıştırıldığı fonksiyondur. Camera Fault Configuration kısmında seçilen özelliklere uygun hatanın, Normal 
        Image Folders kısmında seçilen klasördeki resimlere uygulanıp, FI Image Folder kısmında seçilen klasöre bu hatalı resimlerin
        kaydı işlemini başlatır. 
        
        """

        #### OFFLINE FAULT INJECTION PART ####
        if self.ui.fi_type_combobox.currentText() == "Offline":
            
            print("Processing..")
            # Hata uygulama işlemi başladığında Apply Fault butonu çalışmaz hale getirilir. Hata işlemi tamamlandıktan sonra buton yeniden
            # çalışır hale döndürülür.

            self.ui.apply_fault_button.setEnabled(False)
            self.ui.apply_fault_button.setStyleSheet("background-color: rgb(255, 255, 255);"
                                                        "color: rgb(0, 0, 0);")
            self.ui.apply_fault_button.setText("Processing")
            self.ui.apply_fault_button.setIcon(QtGui.QIcon(":icons/cil-external-link.png"))

            plan_from_list = False  # Kaydedilen plan listesinden plan seçilip uygulama eklendiğinde bu satır kaldırılacak.   
            if plan_from_list == True:
                try:
                    self.ui.info_text.clear()
                    f = open(str(self.get_current_workspace())+'/fi_plans/'+self.fi_plan, "r")
                    self.ui.info_text.setText("FI Plan Applying ...\n-----------------\n"+f.read())
                except:
                    self.pop_up_message('Please choose one fault injection plan from "FI Plans"!')
                else:
                    if self.ui.randomize_check.isChecked() == True:
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
                    normal_image_file = str(file_path)+"/images/normal_image_folders/"+str(self.ui.image_file_tree.selectedIndexes()[0].data())+"/"
                    fi_image_file = str(file_path)+"/images/fault_image_folders/"+str(self.ui.fi_file_tree.selectedIndexes()[0].data())+"/"
                    randomized = self.ui.randomize_check.isChecked()
                    resource, count, fi_image_name_list = ofi(normal_image_file, fi_image_file, self.camera_type, self.fault_type, self.fault_rate, randomized)
                    
                    ###################################
                    # Randomize seçeneği aktifken, sistem rastgele sayıda hatalı resim oluşturur. Hata basılan resimler rastgele seçilir.
                    #   
                    if randomized:
                        self.progress_counter(count)
                        self.ui.info_text.setPlainText(resource+str("\nFault Injected Files:\n")+str(fi_image_name_list))

                    else:
                        self.progress_counter(count)
                        self.ui.info_text.setPlainText(resource)
                except (IndexError):
                    self.pop_up_message("Please choose one Normal and one Fault image folders from Folder Selection Section on the left side.")
                except:
                    self.pop_up_message("Something wrong!")
    
            print("Completed..")

            # Fault uygulama tamamlandığında, Apply Fault butonu eski haline getirilir.
            self.ui.apply_fault_button.setDisabled(False)
            self.ui.apply_fault_button.setStyleSheet("background-color: rgb(6, 37, 98);"
                                                        "color: rgb(255, 255, 255);")
            self.ui.apply_fault_button.setText("Apply Fault")
            self.ui.apply_fault_button.setIcon(QtGui.QIcon(":icons/cil-cloud-upload.png"))
        
        #### REALTIME FAULT INJECTION PART ####
        elif self.ui.fi_type_combobox.currentText() == "Real-time":
            print("Processing..")
            self.ui.info_text.setText("Fault injecting to the ROS camera stream...")
            self.robot_camera = self.ui.ros_cam_topic_text.toPlainText()
            self.pop_up_message("This process will be broken this interface. This will be fixed.")
            
            plan_from_list = False  # Kaydedilen plan listesinden plan seçilip uygulama eklendiğinde bu satır kaldırılacak.   
            
            if plan_from_list == True:
                try:
                    self.ui.info_text.clear()
                    f = open(str(self.get_current_workspace())+'/fi_plans/'+self.fi_plan, "r")
                    self.ui.info_text.setText("FI Plan Applying ...\n-----------------\n"+f.read())
                except:
                    self.pop_up_message('Please choose one fault injection plan from "FI Plans"!')
            else:
                self.info_temp()
                cv2_screen = False # default

                ## Randomized fonksiyonu, realtime modunda CV2 Screen moduna dönüşür. Kullanıcı isterse hata yayınını 
                ## CV2 panelinden ayrıca görüntüleyebilir.

                if self.ui.randomize_check.isChecked() == True:
                    cv2_screen == True
                else:
                    cv2_screen == False

                self.publish_camera = self.robot_camera ## Değişecek.

                try:
                    ## Eğer kullanıcı int bir değer yerine str girişi yaparsa sistem hata mesajı verir, apply_fault çalışmaz.
                    self.fi_freq = int(self.ui.ros_cam_fi_freq_text.toPlainText())
                except ValueError:
                    self.pop_up_message("Please enter a valid frequency value!")
                else:
                    rfi(self.robot_camera, self.publish_camera, self.camera_type, self.fault_type, self.fault_rate, self.fi_freq, cv2_screen)
                

        else:
            self.pop_up_message("Error")
        
    def progress_counter(self, count):
        """
        Progress barını kontrol eden fonksiyondur.
        """
        self.ui.progressBar.setFormat(" ")
        for i in range(count):
            counter = (i/count)*100 + 1
            self.ui.progressBar.setValue(int(counter))
            time.sleep(count/10000)
        self.ui.progressBar.setFormat("Completed")

    def camera_fault_config(self):
        """
        Camera Fault Configuration menusünde tanımlanan özellikleri kaydeden fonksiyondur.

        """

        self.robot_camera_type = self.ui.robot_camera_combobox.currentText()
        self.camera_type = self.ui.camera_type_combobox.currentText()
        self.fi_type = self.ui.fi_type_combobox.currentText()
        self.fault_type = self.ui.fault_type_combobox.currentText()

    def info_temp(self):
        # Bu kısım düzenlenebilir.
        """
        Camera Fault Configuration menusüsünde tanımlanan özellikleri Info bölümüne yazan fonksiyondur. Bunun için configleri temp.txt
        adlı geçici bir dosyaya kaydeder, o dosyadan revize edilen info bilgisini Info sekmesine yazıp temp dosyasını siler.
        """
        try:
            
            
            self.robot_camera_type = self.ui.robot_camera_combobox.currentText()
            self.camera_type = self.ui.camera_type_combobox.currentText()
            self.fi_type = self.ui.fi_type_combobox.currentText()
            self.fault_type = self.ui.fault_type_combobox.currentText()

            if self.fi_type == "Offline":
                f = open("temp.txt", "a")
                f.write("Robot Camera: ")
                f.write(self.robot_camera_type)
                f.write("\nCamera Type: ")
                f.write(self.camera_type)
                f.write("\nFault Inj. Type: ")
                f.write(self.fi_type)
                f.write("\nFault Type: ") 
                f.write(self.fault_type)
                f.write("\nFault Rate: ")
                f.write(self.fault_rate)
                f.write("%")
            else:
                
                self.ros_cam_topic = self.ui.ros_cam_topic_text.toPlainText()
                self.ros_cam_fi_freq = self.ui.ros_cam_fi_freq_text.toPlainText()

                f = open("temp.txt", "a")
                f.write("Robot Camera: ")
                f.write(self.robot_camera_type)
                f.write("\nROS Camera Topic: ")
                f.write(self.ros_cam_topic)
                f.write("\nROS Camera FI Stream Freq: ")
                f.write(self.ros_cam_fi_freq)
                f.write("Hz")
                f.write("\nCamera Type: ")
                f.write(self.camera_type)
                f.write("\nFault Inj. Type: ")
                f.write(self.fi_type)
                f.write("\nFault Type: ") 
                f.write(self.fault_type)
                f.write("\nFault Rate: ")
                f.write(self.fault_rate)
                f.write("%")

        except AttributeError:
            self.pop_up_message("Fault Rate Missing!")

        else:

            if self.fi_type == "Offline":
                if self.ui.randomize_check.isChecked() == True:
                    f.write("\nRandom FI: True")
                elif self.ui.randomize_check.isChecked() == False:
                    f.write("\nRandom FI: False")
                else:
                    pass
            #else:
            #    if self.ui.randomize_check.isChecked() == True:
            #        f.write("\nCV2 Screen: True")
            #    elif self.ui.randomize_check.isChecked() == False:
            #        f.write("\nCV2 Screen: False")
            #    else:
            #        pass 

            f.close()
            f = open("temp.txt", "r")
            self.ui.info_text.setText(f.read())
            f.close()
            os.remove("temp.txt") 

    def save_fi_plan(self):
        """
        Save FI Plan butonunun tanımlandığı fonksiyondur. Camera Fault Config menusünde tanımlanan hata özelliklerini 
        seçilen bir .txt dosyasına kaydeder. Bu kayıt işlemi sonrası onay mesajını Info sekmesinde yayınlar. (Bu kısımda 
        yapılan kayıt sistemi daha sonra .json uzantılı olacak şekilde düzenlenecektir.)
        
        """
        self.info_temp()

        try:
            # S_File will get the directory path and extension.
            S__File = QtWidgets.QFileDialog.getSaveFileName(None,'Save FI Plan',str(self.get_current_workspace())+'/fi_plans/fi_plan', "Text Files (*.txt)")
            
            # This will let you access the test in your QTextEdit
            Text = self.ui.info_text.toPlainText()
            
            #self.fi_plan(Text)

            # This will prevent you from an error if pressed cancel on file dialog.
            if S__File[0]: 
                # Finally this will Save your file to the path selected.
                with open(S__File[0], 'w') as file:
                    date = datetime.datetime.now()
                    file.write("Created: "+str(date.ctime()))
                    file.write("\n----------------------------------\n")
                    file.write(Text)
            
            self.ui.info_text.setText("FI Plan Saved! For Details any Plan, Please Choose One of Them from 'FI Plans' Section and click 'Show FIP Details' button!")

        except (AttributeError):
            self.pop_up_message("Fault Rate Missing!")

        self.update_fi_list_func()

    def pop_up_message(self, msg):
        """
        Demo Tooldaki hata mesajlarını pop up olarak yayınlayan fonksiyondur.

        """
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(msg)
        msgBox.setWindowTitle("Warning")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    def about_section(self):
        """
        About butonunun tanımlandığı fonksiyondur.

        """
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Camera Fault Injection Demo Tool, Oct 2021\nFor More Information, Contact kerem.erdogmus@inovasyonmuhendislik.com.")
        msgBox.setWindowTitle("About")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    
    def help_section(self):
        """
        Help butonunun tanımlandığı fonksiyondur.

        """
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setInformativeText("Welcome to Camera Fault Injector Demo Tool v1.2\n\n")
        msgBox.setDetailedText("""Using this tool you can:
        - You can apply the faults you choose in the configuration menu to the images in the image library you want, and save these wrong images to the folder you want.
        - You can apply these faults to all images as well as to a random number of images, creating a mixed library of faulty images without touching the remaining images.
        - You can save the configuration of the fault you have applied, and view the fault plans you have saved as you wish.
        - You can specify the rate of fault to be applied.
        - For now, three different fault types can be applied offline to images (with .bmp extension) obtained from TOF camera.
       
        """)
        msgBox.setWindowTitle("Help")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

   
    def fault_rate_slider(self):
        """
        Camera Fault Configuration menusündeki Fault Rate değerinin ayarlanmasını sağlayan fonksiyondur.
        Oradaki slider kaydırıldığında istenen rate değeri kutuda görüntülenir. Kutu üzerine yazmaya
        izin verilmez (bu özellik daha sonra eklenebilir ancak slider da buna göre tepki verecek şekilde
        düzenlenmelidir.)

        """
        
        self.fault_rate = str(self.ui.fault_rate_slider.value()+1)
        self.ui.fault_rate_textbrowser.setPlainText(self.fault_rate)

        return self.fault_rate

    def details_fi_list_func(self):
        """
        Update FIP List butonunun tanımlandığı fonksiyondur. FI Plans listesinde yer alan bir plan seçildiğinde bu butonla ilgili
        planın içeriği Info kısmında görüntülenebilir. 
        
        """
        
        try:
            self.ui.info_text.clear()
            self.fi_plan = self.ui.fi_plan_tree.selectedIndexes()[0].data()
            f = open(str(self.get_current_workspace())+'/fi_plans/'+self.fi_plan, "r")
            self.ui.info_text.setText(f.read())
        except:
            self.pop_up_message('Please choose one fault injection plan from "FI Plans"!')

    def read_fi_plans(self, Item):
        self.fi_plan = Item.text()
        print(self.fi_plan)
        return self.fi_plan

    def robot_camera_live(self, robot_camera, publish_camera):
        """
        Real-time hata enjeksiyonunda, yayın yapan kameranın bir başka terminal aracılığıyla açılmasını sağlayan butonun fonksiyonudur.
        """
        
        rc = self.ui.robot_camera_combobox.currentText() # Arayüzde ROS Camera seçili olup olmadığı kontrol edilir.
        
        # Kullanıcı ros_cam_topic_text sekmesine herhangi bir topic ismi girmeden tuşa basarsa bu uyarıyı alır.
        ros_cam_topic_name = self.ui.ros_cam_topic_text.toPlainText()
        if ros_cam_topic_name == "Enter here ROS Camera Topic name ":
            self.pop_up_message('Please enter ROS Camera topic name into the "ROS Cam. Topic" section!')
        else:
            if rc == "ROS Camera":
                # publish_camera da seçilebilir. robot_camera, yayınlanan kameranın topiğini temsil eder, publish_camera ise istenen bir başka
                # topic ismidir.
                robot_camera = self.ui.ros_cam_topic_text.toPlainText()
                os.system("gnome-terminal -x rosrun image_view image_view image:=" + robot_camera) 
            else:
                self.pop_up_message('ROS Camera connection failed.')

    def default_robot_camera_configs(self):
        """
        Robot Camera aktifken açılan konfigürasyon ayarlamalarının arayüz biçimlerini düzenleyen fonksiyondur.
        """
        self.ui.ros_cam_topic_text.setFontItalic(True)
        self.ui.ros_cam_fi_freq_text.setFontItalic(True)
        self.ui.ros_cam_topic_text.setFontPointSize(9.0)
        self.ui.ros_cam_fi_freq_text.setFontPointSize(9.0)
    
    def update_ros_cam_topic_config(self):
        """
        ROS Camera konfigürasyonunda değişiklik yapıldığında fontları ve yazı boyutunu güncelleyen fonksiyondur.
        """
        self.ui.ros_cam_topic_text.setFontItalic(False)
        self.ui.ros_cam_topic_text.setFontPointSize(11.0)
    
    def update_ros_cam_fi_freq_config(self):
        """
        ROS Stream Frequency konfigürasyonunda değişiklik yapıldığında fontları ve yazı boyutunu güncelleyen fonksiyondur.
        """
        self.ui.ros_cam_fi_freq_text.setFontItalic(False)
        self.ui.ros_cam_fi_freq_text.setFontPointSize(11.0)

    def get_current_workspace(self):
        """
            Tool'un çalıştığı workspace konumunu veren fonksiyondur.

        """
        file_full_path = os.path.dirname(os.path.realpath(__file__))

        return file_full_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
