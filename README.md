# pimouse_visual_line_trace
### About
[![](http://img.youtube.com/vi/eLghsLB_j5A/0.jpg)](https://www.youtube.com/watch?v=eLghsLB_j5A)  

### Requirements
 * raspimouse_ros : [https://github.com/ryuichiueda/raspimouse_ros](https://github.com/ryuichiueda/raspimouse_ros)
 * ROS OpenCV camera driver : [https://github.com/OTL/cv_camera](https://github.com/OTL/cv_camera)
* tested Ubuntu Linux 16.04 Mate on Raspberry Pi 3

### Software

If, cv_camera has not
```
sudo apt install ros-kinetic-cv_camera
```

First, move into catkin_ws/src and download this repository.

```
cd ~/catkin_ws/src
git clone https://github.com/masamasa9841/pimouse_visual_line_trace.git
```

Next, catkin_make command

```
cd ~/catkin_ws
catkin_make
```
### Usage
```
rosrun cv_camera cv_camera_node
roslaunch pimouse_visual_line_trace pimouse_visual_line_trace.launch
```
### License

This repository is licensed under the GPLv3 license, see [LICENSE](./LICENSE).

### Reference
[Tiryoh/RaspberryPiMouse](https://github.com/Tiryoh/RaspberryPiMouse)

[ryuichiueda/raspimouse_ros](https://github.com/ryuichiueda/raspimouse_ros)

[DEMURA.NET](http://demura.net/lecture/13067.html)
