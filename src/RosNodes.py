import math

import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose, PoseStamped
from std_msgs.msg import Header
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

def euler_to_quaternion(roll, pitch, yaw):
    """Convert Euler angles to quaternion."""
    qx = math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) - math.cos(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
    qy = math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2)
    qz = math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2) - math.sin(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2)
    qw = math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
    return (qx, qy, qz, qw)

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

        self.icrPublisher = self.create_publisher(
            PoseStamped,
            topicPrefix + '/icr',
            10)


        self.odomPublisher = self.create_publisher(
            Odometry,
            topicPrefix + '/odom',
            10)

        self.lidarPublisher = self.create_publisher(
            LaserScan,
            topicPrefix + '/lidar',
            10)

        self.tf_broadcaster = TransformBroadcaster(self)

        self.timer = self.create_timer(0.5, self.timerCallback)

    def broadcastTransform(self):
        # Broadcast TF
        transform = TransformStamped()
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_link'
        transform.header.stamp = self.get_clock().now().to_msg()

        transform.transform.translation.x = self.vehicle.pos.x/100
        transform.transform.translation.y = self.vehicle.pos.y/100
        transform.transform.translation.z = 0.0

        # Set rotation
        q = euler_to_quaternion(0, 0, math.radians(self.vehicle.getAngle()))
        transform.transform.rotation.x = q[0]
        transform.transform.rotation.y = q[1]
        transform.transform.rotation.z = q[2]
        transform.transform.rotation.w = q[3]

        # Broadcast the transform
        self.tf_broadcaster.sendTransform(transform)

    def publishOdometry(self):
        msg = Odometry()

        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"
        msg.child_frame_id = "odom"

        msg.pose.pose.position.x = self.vehicle.pos.x/100
        msg.pose.pose.position.y = self.vehicle.pos.y/100
        msg.pose.pose.position.z = float(0)

        q = euler_to_quaternion(0, 0, math.radians(self.vehicle.getAngle()))
        msg.pose.pose.orientation.x = q[0]
        msg.pose.pose.orientation.y = q[1]
        msg.pose.pose.orientation.z = q[2]
        msg.pose.pose.orientation.w = q[3]

        self.odomPublisher.publish(msg)

    def publishPose(self):
        msg = Pose()
        msg.position.x = self.vehicle.pos.x/100
        msg.position.y = self.vehicle.pos.y/100
        msg.position.z = float(0)

        q = euler_to_quaternion(0, 0, math.radians(self.vehicle.getAngle()))
        msg.orientation.x = q[0]
        msg.orientation.y = q[1]
        msg.orientation.z = q[2]
        msg.orientation.w = q[3]

        self.posePublisher.publish(msg)

    def publishIcr(self):
        msg = PoseStamped()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        radSteering = math.radians(self.vehicle.steeringAngle)
        if radSteering == 0:
            return
        icrY = self.vehicle.wheelBase / math.tan(radSteering)

        rads = math.radians(math.pi /2 - self.vehicle.angle)
        pIcrX = 0 * math.cos(rads) - icrY * math.sin(rads)
        pIcrY = 0 * math.sin(rads) + icrY * math.cos(rads)
        print(f"ICR: {pIcrX}, {pIcrY}")
        msg.pose.position.x = pIcrY/100
        msg.pose.position.y = pIcrX/100
        msg.pose.position.z = float(0)

        q = euler_to_quaternion(0, math.radians(-90), 0)
        msg.pose.orientation.x = q[0]
        msg.pose.orientation.y = q[1]
        msg.pose.orientation.z = q[2]
        msg.pose.orientation.w = q[3]

        self.icrPublisher.publish(msg)

    def publishLidar(self, scan, lidar, angle, scanTime):
        msg = LaserScan()
        msg.header = Header()
        #TODO: Timestamp this properlly
        msg.header.stamp = self.get_clock().now().to_msg()
        #msg.header.stamp.nanosec = 0
        msg.header.frame_id = "base_link"
        #msg.header.frame_id = "odom"

        msg.angle_min = math.radians(0)
        msg.angle_max = math.radians(lidar.numRays * lidar.rayAngleIncrement)
        msg.angle_increment = math.radians(lidar.rayAngleIncrement)

        msg.time_increment = 0.0
        msg.scan_time = scanTime

        msg.range_min = 0.0
        msg.range_max = float('inf')

        msg.ranges = scan
        msg.intensities = []

        self.lidarPublisher.publish(msg)

    def timerCallback(self):
        #self.publishPose()
        self.publishIcr()
        self.publishOdometry()
        self.broadcastTransform()

    def listener_callback(self, msg):
        self.vehicle.setThrottle(msg.linear.x)
        self.vehicle.setSteering(msg.angular.z*2)
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

