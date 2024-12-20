import math

import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose
from std_msgs.msg import Header
from sensor_msgs.msg import LaserScan

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

        self.lidarPublisher = self.create_publisher(
            LaserScan,
            topicPrefix + '/lidar',
            10)

        self.timer = self.create_timer(0.5, self.timerCallback)

    def generateQuaternion(self):
        yaw = self.vehicle.getAngle()
        x = 0.0
        y = 0.0
        z = math.sin(yaw/2.0)
        w = math.cos(yaw/2.0)
        return (x, y, z, w)

    def publishPose(self):
        msg = Pose()
        msg.position.x = self.vehicle.pos.x
        msg.position.y = self.vehicle.pos.y
        msg.position.z = float(0)

        q = self.generateQuaternion()
        msg.orientation.x = q[0]
        msg.orientation.y = q[1]
        msg.orientation.z = q[2]
        msg.orientation.w = q[3]

        self.posePublisher.publish(msg)

    def publishLidar(self, scan, lidar, angle, scanTime):
        msg = LaserScan()
        msg.header = Header()
        #TODO: Timestamp this properlly
        msg.header.stamp = self.get_clock().now().to_msg()
        #msg.header.stamp.nanosec = 0
        msg.header.frame_id = "base_link"

        msg.angle_min = math.radians(0)
        msg.angle_max = math.radians(lidar.numRays * lidar.rayAngleIncrement)
        msg.angle_increment = math.radians(-lidar.rayAngleIncrement)

        msg.time_increment = 0.0
        msg.scan_time = scanTime

        msg.range_min = 0.0
        msg.range_max = float('inf')

        msg.ranges = scan
        msg.intensities = []

        self.lidarPublisher.publish(msg)

    def timerCallback(self):
        self.publishPose()

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
        rclpy.init()
        self.node = TwistSubscriber(self.vehicle, self.topicPrefix)

        self.thread = threading.Thread(target=self.startNode)
        self.thread.start()

    def startNode(self):
        rclpy.spin(self.node)

