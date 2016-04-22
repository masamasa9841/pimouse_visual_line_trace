#
# p.py
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
import sys
import rospy
import time
import numpy as np
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from raspimouse_ros.srv import SwitchMotors

class line_trace:
    def __init__(self):
        signal.signal(signal.SIGINT, self.handler)
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size = 10)
        sub = rospy.Subscriber('/e', Float64, self.callback, queue_size=10)
        sub2 = rospy.Subscriber('/center', Float64, self.callback2, queue_size=10)
        self.vel = Twist()
        rospy.sleep(1)
    
    def handler(self, signal, frame):
        if not self.switch_motors(False):
            print "[check failed]: motors are not turned off"
        sys.exit(0)

    def switch_motors(self, onoff):
        rospy.wait_for_service('/switch_motors')
        try:
            p = rospy.ServiceProxy('/switch_motors', SwitchMotors)
            res = p(onoff)
            return res.accepted
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e
        else:
            return False

    def callback(self, msg):
        self.e = msg.data

    def callback2(self, msg):
        self.center = msg.data

    def main(self):
        if not self.switch_motors(True):
            print "[check failed]: motors are not empowered"
        while not rospy.is_shutdown():
            e = 320 - self.center
            vel = abs(self.e)
            self.vel.angular.z = e * 0.0045
            if vel > 30 : vel  = 30
            self.vel.linear.x = -(50 - vel) * 0.004
            self.pub.publish(self.vel)

if __name__ == '__main__':
    rospy.init_node('line_trace', anonymous = True)
    lt = line_trace()
    lt.main()
