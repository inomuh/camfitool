## Camera Fault Injection Demo Tool

This tool is a simple interface that allows injection of image faults into robot cameras. Thanks to this interface, you can create new image libraries by injecting the fault types you have determined, both real-time to TOF and RGB type ROS cameras, and to the image libraries previously recorded by these cameras. For more information about the purpose of this tool: https://arxiv.org/abs/2108.13803

![Image of CamFIDemoTool](https://github.com/inomuh/Camera-Fault-Injection-Demo-Tool/blob/main/camfidemotool_v1.1.png)

### Tool Features (in v1.1)
---------------------------
- You can apply the faults you choose in the configuration menu to the images in the image library you want, and save these wrong images to the folder you want.
- You can apply these faults to all images as well as to a random number of images, creating a mixed library of faulty images without touching the remaining images.
- You can save the configuration of the fault you have applied, and view the fault plans you have saved as you wish.
- You can specify the rate of fault to be applied.
- For now, three different fault types can be applied offline to images (with .bmp extension) obtained from TOF camera.

Changelog:
----------
Update v1.1 - 03.11.21
------------------------
- First Commit

---------------------------------------------------------------------------------
Roadmap For Next Updates:
-------------------------
* [x] Offline Type Fault Injection
* [x] TOF Camera FI
* [x] Randomized FI Feature
* [x] Three Fault Types (Salt&Pepper, Gaussian, Poisson)
* [ ] RGB Camera FI
* [ ] Real-Time Type Fault Injection
* [ ] ROS Noetic Integration
