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
        rospy.sleep(0.5)
    
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
            e = 320 -self.center
            vel = abs(self.e)
            self.vel.angular.z = e * 0.0055
            if vel > 30 : vel  = 30
            self.vel.linear.x = -(50 - vel) * 0.0035
            self.pub.publish(self.vel)

if __name__ == '__main__':
    rospy.init_node('line_trace', anonymous = True)
    lt = line_trace()
    lt.main()
