import math

import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose

class TwistSubscriber(Node):
    def __init__(self, vehicle, topicPrefix):
        super().__init__('twist_subscriber')
        self.vehicle = vehicle
        self.subscription = self.create_subscription(
            Twist,
            topicPrefix + '/cmd_vel',
            self.listener_callback,
            10)

        self.posePublisher = self.create_publisher(
            Pose,
            topicPrefix + '/pose',
            10)

        self.timer = self.create_timer(0.5, self.timerCallback)

    def generateQuaternion(self):
        yaw = self.vehicle.getAngle()
        x = 0.0
        y = 0.0
        z = math.sin(yaw/2.0)
        w = math.cos(yaw/2.0)
        return (x, y, z, w)

    def timerCallback(self):
        msg = Pose()
        msg.position.x = self.vehicle.x
        msg.position.y = self.vehicle.y
        msg.position.z = float(0)

        q = self.generateQuaternion()
        msg.orientation.x = q[0]
        msg.orientation.y = q[1]
        msg.orientation.z = q[2]
        msg.orientation.w = q[3]

        self.posePublisher.publish(msg)

    def listener_callback(self, msg):
        self.vehicle.setThrottle(msg.linear.x)
        self.vehicle.setSteering(-msg.angular.z)
        self.get_logger().info(f'Received twist message: linear={msg.linear.x, msg.linear.y, msg.linear.z}, angular={msg.angular.x, msg.angular.y, msg.angular.z}')

class RosNode:
    def __init__(self, vehicle, topicPrefix):
        self.node = None
        self.thread = None
        self.vehicle = vehicle
        self.topicPrefix = topicPrefix

    def start(self):
        self.thread = threading.Thread(target=self.startNode)
        self.thread.start()

    def startNode(self):
        rclpy.init()
        self.node = TwistSubscriber(self.vehicle, self.topicPrefix)
        rclpy.spin(self.node)

