# Camera Fault Injection Tool
![Documentation](https://img.shields.io/badge/Docs-http%3A%2F%2Fwiki.ros.org%2Fcamfitool%2F-brightgreen)
[![CodeFactor](https://www.codefactor.io/repository/github/akerdogmus/camfitool/badge)](https://www.codefactor.io/repository/github/akerdogmus/camfitool)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

![current_version](https://img.shields.io/github/v/release/inomuh/camfitool?color=green) ![last_commit](https://img.shields.io/github/last-commit/inomuh/Camera-Fault-Injection-Tool?color=green) ![tool version](https://img.shields.io/badge/version-standart-blue) ![repo_size](https://img.shields.io/github/repo-size/inomuh/Camera-Fault-Injection-Tool) ![Apache-2.0 License](https://img.shields.io/github/license/inomuh/Camera-Fault-Injection-Tool?color=blue) ![lang](https://img.shields.io/github/languages/top/inomuh/camfitool)

This tool is a simple interface that allows injection of image faults into robot cameras. Thanks to this interface, you can create new image libraries by injecting the fault types you have determined, both real-time to TOF and RGB type ROS cameras, and to the image libraries previously recorded by these cameras. For more information about the purpose of this tool: https://arxiv.org/abs/2108.13803

Developed by Alim Kerem Erdogmus from Inovasyon Muhendislik (c) 2021

ROS Wiki page: http://wiki.ros.org/camfitool

For trying ROS package version of CamFITool:

    git clone https://github.com/inomuh/camfitool -b noetic-version
    

![Image of CamFIDemoTool_v1.2_offline](https://github.com/inomuh/Camera-Fault-Injector-Tool/blob/v1.2/camfitool_v1.2_offline.png)
*Fig 1. Camera Fault Injector Tool Offline FI Configuration*

![Image of CamFIDemoTool_v1.2_realtime](https://github.com/inomuh/Camera-Fault-Injector-Tool/blob/v1.2/camfitool_v1.2_realtime.png)
*Fig 2. Camera Fault Injector Tool Realtime FI Configuration*

### Tool Features (in v1.3)
---------------------------
- You can apply the faults you choose in the configuration menu to the images in the image library you want, and save these wrong images to the folder you want. So you can create your faulty image library.
- You can apply these faults to all images as well as to a random number of images, creating a mixed library of faulty images without touching the remaining images (only offline fault application).
- You can save the configuration of the fault you have applied, and view the fault plans you have saved as you wish.
- You can specify the rate of fault to be applied.
- Three different fault types can be applied offline to images (with .bmp extension) obtained from TOF camera and six different fault types can be applied offline to images (with .png/.jpg extension) obtained from RGB camera.
- **NEW** It is now possible to select what percentage of images in the normal image database to apply an error.
- **NEW** It is possible to inject two different error types into a normal image database at desired rates (it is not possible to apply more than two errors to the same database yet).
- For now, six different fault types can be applied real-time stream obtained from RGB camera (TOF Realtime FI will be added).
- You can use the ROS Noetic version (noetic-version) or the standard version (current v1.2.3).
- You can monitor the ROS Camera node.
- You can specify the rate of real-time fault injecting frequency to be applied.

---

![Image of CamFIDemoTool_v1.2_realtime_openfi_appliying](https://github.com/inomuh/Camera-Fault-Injector-Tool/blob/v1.2/camfitool_v1.2_realtime_openfi_applying.png)
*Fig 3. Camera Fault Injector Tool Realtime FI Applying Demonstration*

Changelog:
----------
Update v1.1 - 03.11.21
------------------------
- First Commit

Update v1.2 - 10.11.21
------------------------
- Added Real-time FI mode
- Added RGB Camera FI types (Open, Close, Erosion, Dilation, Gradient and Motion-blur). Now this interface supports two camera types and nine fault types.
- Added Robot Cam button. This button provides to show active ROS camera (tried ROS Noetic) screen (User must enter ROS Camera topic name).
- Robot Camera section is active now. User can enter ROS camera topic name for fault injection and enter ROS fault injecting stream frequency value.
- Added Real-time FI plan saving standart. This plan saving is different than Offline FI plan ones.
- Some bug fixes, new error pop-up messages and other things.

Update v1.2.1 - 01.12.21
------------------------
- Added Error Log system.
- Fixed randomized fault injection function issue.

Update v1.2.2 - 03.12.21
------------------------
- CamFITool's software codes are revised (using [Pylint](https://pylint.org/) and [Prospector](https://pypi.org/project/prospector/)).

Update v1.2.3 - 06.12.21
------------------------
- Fixed "Known Issues #4: Offline RGB Randomized FI crash" bug
- Fixed "Known Issues #3: Image Formats"
- New image databases added (These images taken from [COIL Database](https://www1.cs.columbia.edu/CAVE/software/softlib/coil-100.php))

Update v1.3 - 17.01.22
------------------------
- CamFITool main codes are revised.
- Two different fault types can now be injected into the same output folder (Max two fault type).
- An fault can now be injected into a certain rate of an image database (Fault Implementation Rate).
- Reset button added (You can reset the interface with this).
- Some bug fixes.

---------------------------------------------------------------------------------
Roadmap For Next Updates:
-------------------------
* [x] Offline Type Fault Injection
* [x] TOF Camera FI
* [x] Randomized FI Feature
* [x] Three Fault Types (Salt&Pepper, Gaussian, Poisson)
* [x] RGB Camera FI
* [x] Real-Time Type Fault Injection (only RGB cameras)
* [x] +6 Fault Types (Open, Close, Dilation, Erosion, Gradient and Motionblur)
* [x] [Github Wiki page](https://github.com/inomuh/camfitool/wiki)
* [x] [ROS Wiki page](http://wiki.ros.org/camfitool/)
* [x] [CamFITool Pypi package](https://pypi.org/project/camfitool/) (This is Alpha version)
* [x] Reset Button
* [x] Mixed Fault Injection
* [ ] Real-Time TOF Faults integration
* [ ] CV2 Screen option
* [x] ROS Noetic Integration
* [ ] More Fault Types
* [ ] ROS2 Integration
* [x] Error Log System
* [ ] Improved Help Section
* [x] [CamFITool ROS Package version](https://github.com/inomuh/camfitool/tree/noetic-version)

### Credits

<a href="http://valu3s.eu">
  <img align=left img src="https://upload.wikimedia.org/wikipedia/tr/d/d0/TUBITAK-Logo.jpg" 
       alt="tübitak_logo" height="100" >
</a>

---

This work is supported by [TÜBİTAK](https://www.tubitak.gov.tr/) Project under grant number 120N803 which conducted by the İnovasyon Mühendislik.

---

<a href="http://valu3s.eu">
  <img align=right img src="https://valu3s.eu/wp-content/uploads/2020/04/VALU3S_green_transparent-1024x576.png" 
       alt="valu3s_logo" height="100" >
</a>

  This work is also done by [Inovasyon Muhendislik](https://www.inovasyonmuhendislik.com/) under [VALU3S](https://valu3s.eu) project. This project has received funding from the [ECSEL](https://www.ecsel.eu) Joint Undertaking (JU) under grant agreement No 876852. The JU receives support from the European Union’s Horizon 2020 research and innovation programme and Austria, Czech Republic, Germany, Ireland, Italy, Portugal, Spain, Sweden, Turkey.

## Cite

If the code or data help you, please cite the following the paper.

    @article{erdogmus2021manipulation,
      title={Manipulation of Camera Sensor Data via Fault Injection for Anomaly Detection Studies in Verification and Validation Activities For AI},
      author={Erdogmus, Alim Kerem and Karaca, Mustafa and others},
      journal={arXiv preprint arXiv:2108.13803},
      year={2021}
    }

### License

See the [LICENSE](LICENSE.md) file for license rights and limitations (Apache-2.0 Licence).
