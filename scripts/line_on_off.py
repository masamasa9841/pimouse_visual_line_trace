#
# line_on_off.py
# visual line trace
#
# Copyright (C) 2017 MasayaOkawa <masamasa9841@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
# 
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import cv2
import time
import numpy as np
from geometry_msgs.msg import Twist
from std_msgs.msg import String, UInt16
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from raspimouse_ros.srv import *
from raspimouse_ros.msg import *
from std_msgs.msg import UInt16

class line_trace:
    def __init__(self):
        image = rospy.Subscriber('/cv_camera/image_raw', Image, self.callback, queue_size = 1)
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size = 10)
        self.bridge = CvBridge()
        self.vel = Twist()
        rospy.sleep(0.5)

    def callback(self, data):
        try:
            image = self.bridge.imgmsg_to_cv2(data, "bgr8") 
        except CvBridgeError as error:
            print error
        mask = self.mask_image(image)
        image, self.e, self.center =  self.add_point_and_line(image, mask)
        self.display(image, mask)

    def mask_image(self, data):
        #change rgb to hsv
        hsv_image = cv2.cvtColor(data, cv2.COLOR_BGR2HSV)
        color_min = np.array([0, 0, 0])
        color_max = np.array([180, 180, 90])
        color_mask = cv2.inRange(hsv_image, color_min, color_max)
        return color_mask

    def add_point_and_line(self, image, mask):
        width = mask.shape[1]
        height = mask.shape[0]
        line_1 = height / 2
        line_2 = int(height / 2 * 0.8)
        #line
        image = cv2.line(image, (0, line_1), (width, line_1), (255, 0, 0), 2)
        image = cv2.line(image, (0, line_2), (width, line_2), (0, 0, 255), 2)
        #point
        count = [0,0] 
        sensor_data = [0,0] 
        for i in range(width):
            if mask[line_1, i]:
                count[0] += 1
                sensor_data[0] += i
            if mask[line_2, i]:
                count[1] += 1
                sensor_data[1] += i
        if count[0] != 0 and count[1] != 0: 
            point_1 = sensor_data[0] / count[0] 
            point_2 = sensor_data[1] / count[1] 
            image = cv2.circle(image, (point_1, line_1), 5, (0, 255, 0))
            image = cv2.circle(image, (point_2, line_2), 5, (0, 255, 0))
            #slope line
            image = cv2.line(image, (point_1, line_1), (point_2, line_2), (0, 255, 0), 2)
            #to pid
            e = point_2 - point_1
            center = (point_2 + point_1) / 2
        else: 
            rospy.loginfo("No line")
            e = 0
            center = 0
        return image, e, center

    def display(self, data, data2):
        #Fix window size
        cv_half_image = cv2.resize(data, (0,0), fx = 0.5, fy = 0.5)
        cv_half_image2 = cv2.resize(data2, (0,0), fx = 0.5, fy = 0.5)
        #Display window
        cv2.imshow("Image", cv_half_image)
        cv2.imshow("Image2", cv_half_image2)
        cv2.waitKey(3)

    def raw_control(self, left_hz,right_hz):
        pub = rospy.Publisher('/motor_raw', MotorFreqs, queue_size=10)

        if not rospy.is_shutdown():
            d = MotorFreqs()
            d.left = left_hz
            d.right = right_hz
            pub.publish(d)

    def main(self):
        while not rospy.is_shutdown():
            #print self.e
            print self.center
            if 320 - self.center > 0:
                self.raw_control(-100,0)
            else:
                self.raw_control(0,-100)
            time.sleep(0.2)
            #self.raw_control(0,0)
            #time.sleep(0.1)
        cv2.destroyAllWindows()

if __name__ == '__main__':
    rospy.init_node('line_trace', anonymous = True)
    lt = line_trace()
    lt.main()
