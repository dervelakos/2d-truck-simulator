import socket
import struct
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Header
import nav_msgs
from nav_msgs.msg import OccupancyGrid

from MiddlewareBuffer import MiddlewareBuffer
from Middleware import InputDataStream
from CommMsgs import PoseMsg, LidarMsg

from OccupancyGrid import OccupancyGrid as Ocg

# Multicast group configuration
MCAST_GRP = '224.1.1.1'   # Local multicast address
MCAST_PORT = 5007          # Port to listen on

rclpy.init()

class RosPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.lidarPublisher = self.create_publisher(
            LaserScan,
            '/vehicle2/lidar',
            10)

        self.gridPublisher = self.create_publisher(
            OccupancyGrid,
            '/vehicle2/grid',
            10)

    def publishLidar(self, lidarMsg):
        msg = LaserScan()
        msg.header = Header()
        #TODO: Timestamp this properlly
        msg.header.stamp = self.get_clock().now().to_msg()
        #msg.header.stamp.nanosec = 0
        msg.header.frame_id = "base_link"
        #msg.header.frame_id = "odom"

        msg.angle_min = lidarMsg.angle_min
        msg.angle_max = lidarMsg.angle_max
        msg.angle_increment = lidarMsg.angle_increment

        msg.time_increment = 0.0
        msg.scan_time = 1.0

        msg.range_min = 0.0
        msg.range_max = float('inf')

        msg.ranges = lidarMsg.ranges #[x / 100 for x in lidarMsg.ranges]
        msg.intensities = []

        self.lidarPublisher.publish(msg)

    def publishOccupancyGrid(self, grid):
        msg = OccupancyGrid()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        msg.info.map_load_time = self.get_clock().now().to_msg()
        msg.info.resolution = grid.getResolution()
        msg.info.width = grid.getWidth()
        msg.info.height = grid.getHeight()

        orig = grid.getOrigin()
        msg.info.origin.position.x = orig[0]
        msg.info.origin.position.y = orig[1]
        msg.info.origin.position.z = 0.0
        msg.info.origin.orientation.x = 0.0
        msg.info.origin.orientation.y = 0.0
        msg.info.origin.orientation.z = 0.0
        msg.info.origin.orientation.w = 1.0

        msg.data = grid.getData()

        self.gridPublisher.publish(msg)

stream1 = InputDataStream(MCAST_GRP, MCAST_PORT)
stream2 = InputDataStream(MCAST_GRP, MCAST_PORT+1)
ros = RosPublisher()
grid = Ocg(0.1)
try:
    while True:
        # Receive Pose
        buffer = stream1.recv(28)
        msg = PoseMsg()
        msg.loadPose(buffer)
        msg.printPose()

        # Receive Lidar scan
        buffer = stream2.recv(2892)
        msg1 = LidarMsg()
        msg1.loadScan(buffer)
        #msg.printScan()

        #Forward Lidar scan
        ros.publishLidar(msg1)

        grid.processScan(msg1, msg)
        ros.publishOccupancyGrid(grid)
        print("Loop")
        #time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    stream1.close()
    stream2.close()

