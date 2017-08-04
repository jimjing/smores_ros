#!/usr/bin/env python
import rospy
import tf
import time
import sys
import numpy as np
from std_msgs.msg import Int32, String
from geometry_msgs.msg import Vector3, Pose, Twist
from smores_ros.srv import set_behavior

class BlockController(object):
    def __init__(self):
        self.param_dict = {}
        self.param_name_list = []
        self.cmd_vel_pub = None
        self.tf = None
        self.rate = None
        self.first_tag = ""
        self.middle_tag = ""
        self.last_tag = ""


        self._initialize()
        self.main()

    def _getROSParam(self):
        for para_name in self.param_name_list:
            if rospy.has_param(para_name):
                self.param_dict[para_name.lstrip("~")] = rospy.get_param(para_name)
            else:
                rospy.logerr("Cannot find parameter {}.".format(para_name))

    def _initialize(self):
        self.param_name_list = ["~set_behavior_service_name",
                                "~drive_command_topic_name",
                                "~test_apriltags",
                                ]
        self._getROSParam()
        self.tf = tf.TransformListener()
        self.rate = rospy.Rate(10)
        self.first_tag = "tag_5"
        self.middle_tag = "tag_6"
        self.last_tag = "tag_7"


        if self.param_dict["test_apriltags"]:
            rospy.loginfo("Apriltag testing mode ...")
        else:
            # Setup client, publishers and subscribers
            self.cmd_vel_pub = rospy.Publisher(
                    self.param_dict["drive_command_topic_name"], Twist, queue_size=1)

            # Waiting for all service to be ready
            rospy.loginfo("Waiting for set behavior service ...")
            rospy.wait_for_service(self.param_dict["set_behavior_service_name"])

    def _test_apriltags(self):
        move_tag = self.first_tag
        while not rospy.is_shutdown():
            self.rate.sleep()
            try:
                (move_pose, move_rot) = self.getTagPosition("goal")
            except TypeError as e:
                rospy.logerr("Cannot find position for {!r}: {}".format(move_tag, e))
                continue

            theta = tf.transformations.euler_from_quaternion(move_rot, 'szyx')[2]
            rospy.loginfo("Pose is {:.4f} and {:.4f} and {:.4f}".format(move_pose[0], move_pose[1], theta))

    def adjustAlignment(self):
        _last_direction = ""
        while not rospy.is_shutdown():
            self.rate.sleep()
            try:
                (move_pose, move_rot) = self.getTagPosition(self.last_tag)
            except TypeError as e:
                rospy.logerr("Cannot find position for {!r}: {}".format(self.last_tag, e))
                continue

            theta = tf.transformations.euler_from_quaternion(move_rot, 'szyx')[0]
            rospy.loginfo("Pose is {:.4f} and {:.4f} and {:.4f}".format(move_pose[0], move_pose[1], theta))

            if abs(abs(theta) - np.pi/2) < 0.01:
                # We are at good alignment
                self.setBehavior("ShortSnake", "stop", True)
                self.adjustHeadTilt()
            else:
                # Need to adjust alignment
                if abs(theta) > np.pi/2:
                    # Turn cw
                    if _last_direction == "cw":
                        continue
                    else:
                        self.setBehavior("ShortSnake", "spinCW", True)
                        _last_direction = "cw"
                else:
                    # Turn ccw
                    if _last_direction == "ccw":
                        continue
                    else:
                        self.setBehavior("ShortSnake", "spinCCW", True)
                        _last_direction = "ccw"

    def adjustHeadTilt(self):
        _last_direction = ""
        while not rospy.is_shutdown():
            self.rate.sleep()
            try:
                (move_pose, move_rot) = self.getTagPosition(self.first_tag)
            except TypeError as e:
                rospy.logerr("Cannot find position for {!r}: {}".format(self.first_tag, e))
                continue

            theta = tf.transformations.euler_from_quaternion(move_rot, 'szyx')[2]
            rospy.loginfo("Pose is {:.4f} and {:.4f} and {:.4f}".format(move_pose[0], move_pose[1], theta))

            if abs(theta - 0.0) < 0.01:
                # We are at good tilt
                self.setBehavior("ShortSnake", "stop", True)
                self.setBehavior("ShortSnake", "openDrawer", True)
                rospy.logerr("Done!")
                sys.exit(0)
            else:
                # Need to adjust tilt
                if theta > 0.0:
                    # Turn down
                    if _last_direction == "down":
                        continue
                    else:
                        self.setBehavior("ShortSnake", "adjustHeadTiltDOWN", True)
                        _last_direction = "down"
                else:
                    # Turn up
                    if _last_direction == "up":
                        continue
                    else:
                        self.setBehavior("ShortSnake", "adjustHeadTiltUP", True)
                        _last_direction = "up"

    def main(self):
        if self.param_dict["test_apriltags"]:
            self._test_apriltags()

        if rospy.is_shutdown():
            return

        ## Set configuration
        #self.setBehavior("Arm", "", True)
        ## Lift the front face
        #self.setBehavior("Arm", "dropRamp", True)
        ## Break sensor box connection
        #self.setBehavior("Arm", "breakSensorBox", True)
        ## Stand up the shortsnake
        #self.setBehavior("ShortSnake", "", True)
        #self.setBehavior("ShortSnake", "stand", True)
        #time.sleep(1)
        ## Move the shortsnake
        #self.setBehavior("ShortSnake", "forward", True)
        ## Move the sensor box
        #self.setBehavior("Arm", "", True)
        #self.setBehavior("Arm", "pushSensor", True)
        ## Wait for 8 seconds
        #time.sleep(8)
        ## Stop the sensor box
        #self.setBehavior("Arm", "stop", True)
        ## Resume climbing
        #self.setBehavior("ShortSnake", "", True)
        #self.setBehavior("ShortSnake", "forward", True)
        ## Now bend shortsnake more
        #self.setBehavior("ShortSnake", "bend", True)

        #while not rospy.is_shutdown():
        #    self.rate.sleep()
        #    try:
        #        (move_pose, move_rot) = self.getTagPosition(self.middle_tag)
        #    except TypeError as e:
        #        rospy.logerr("Cannot find position for {!r}: {}".format(self.middle_tag, e))
        #        continue

        #    theta = tf.transformations.euler_from_quaternion(move_rot, 'szyx')[1]
        #    rospy.loginfo("Pose is {:.4f} and {:.4f} and {:.4f}".format(move_pose[0], move_pose[1], theta))

        #    # Check if the car is in position or not
        #    if move_pose[0] < -0.14:
        #        self.setBehavior("ShortSnake", "stop", True)
        #        rospy.loginfo("Arrived")

        #        # Prepare to spin in place
        #        self.setBehavior("ShortSnake", "preSpin", True)

        #        # Spin until it is aligned with drawer
        #        self.adjustAlignment()

        self.setBehavior("Arm", "drive", False)

        back_up_counter = 0
        _last_drive = False
        t = "goal"
        while not rospy.is_shutdown():
            self.rate.sleep()
            try:
                (move_pose, move_rot) = self.getTagPosition(t)
            except TypeError as e:
                rospy.logerr("Cannot find position for {!r}: {}".format(t, e))
                continue

            theta = tf.transformations.euler_from_quaternion(move_rot, 'szyx')[1]
            rospy.loginfo("Pose is {:.4f} and {:.4f} and {}".format(move_pose[0], move_pose[1], theta))

            if back_up_counter > 3:
                # Backup
                _last_drive = False
                data = Twist()
                data.linear.x = -0.1
                self.cmd_vel_pub.publish(data)
                time.sleep(3)
                back_up_counter = 0

            if move_pose[1] > 0.01 or move_pose[1] < -0.01:
                if _last_drive:
                    _last_drive = False
                    if t == "tag_2":
                        back_up_counter += 1
                self.doVisualServo(move_pose[0], move_pose[1])
            else:
                # Drive forward
                _last_drive = True
                data = Twist()
                data.linear.x = 0.1
                self.cmd_vel_pub.publish(data)
                if t == "goal":
                    dist = 0.0
                    tol = 0.20
                if t == "tag_2":
                    dist = 0.03
                    tol = 0.01
                if abs(move_pose[0] - dist) <tol:
                    if t == "goal":
                        t = "tag_2"
                    else:
                        rospy.logerr("Picking up")
                        self.setBehavior("", "", False)
                        self.setBehavior("Arm", "pickUp", True)
                        time.sleep(5)
                        self.setBehavior("", "", False)
                        return

    def getTagPosition(self, tag_id):
        rospy.logdebug("Getting position for {!r}".format(tag_id))
        while not rospy.is_shutdown():
            try:
                return self.tf.lookupTransform("tag_5",tag_id, rospy.Time(0))
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as e:
                rospy.logerr(e)
                return None

    def setBehavior(self, configuration_name, behavior_name, is_action=False):
        try:
            set_behavior_service = rospy.ServiceProxy(
                    self.param_dict["set_behavior_service_name"], set_behavior)
            resp = set_behavior_service(configuration_name, behavior_name, is_action)
            return resp.status
        except rospy.ServiceException, e:
            rospy.logerr("Service call failed: {}".format(e))

    def doVisualServo(self, x, y):
        data = Twist()
        if y > 0.01:
            # Turn left
            rospy.logdebug("Turning left")
            data.angular.z = 0.3
            self.cmd_vel_pub.publish(data)
        elif y < -0.01:
            # Turn right
            rospy.logdebug("Turning right")
            data.angular.z = -0.3
            self.cmd_vel_pub.publish(data)
