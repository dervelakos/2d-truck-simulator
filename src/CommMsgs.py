import math

from MiddlewareBuffer import MiddlewareBuffer

def euler_to_quaternion(roll, pitch, yaw):
    """Convert Euler angles to quaternion."""
    qx = math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) - math.cos(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
    qy = math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2)
    qz = math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2) - math.sin(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2)
    qw = math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
    return (qx, qy, qz, qw)

class LidarMsg:
    def __init__(self):
        self.angle_min = math.radians(0)
        self.angle_max = math.radians(0)
        self.angle_increment = math.radians(0)
        self.ranges = [] # 360 values
        self.intensities = [] # 360 values

    def fillBuffer(self, buffer, scan, lidar, angle, scanTime):
        buffer.addFloat32(math.radians(0))
        buffer.addFloat32(math.radians(lidar.numRays * lidar.rayAngleIncrement))
        buffer.addFloat32(math.radians(lidar.rayAngleIncrement))

        for entry in scan:
            buffer.addFloat32(entry)

    def loadScan(self, buffer: MiddlewareBuffer):
        self.angle_min = buffer.readNextFloat32()
        self.angle_max = buffer.readNextFloat32()
        self.angle_increment = buffer.readNextFloat32()
        self.ranges = [buffer.readNextFloat32() / 100.0 for _ in range(360)]
        self.intensities = []

    def printScan(self):
        for entry in self.ranges:
            print(entry)

class PoseMsg:

    def __init__(self):
        self.position = [0.0, 0.0, 0.0]
        self.orientation = [0.0, 0.0, 0.0, 0.0]

    def storePose(self, obj):
        """Store pose from the external object locally"""
        # Position
        self.position[0] = obj.pos.x / 100
        self.position[1] = obj.pos.y / 100
        self.position[2] = 0.0  # z fixed to 0

        # Orientation: convert Euler to quaternion
        angle_rad = math.radians(obj.getAngle())
        q = euler_to_quaternion(0, 0, angle_rad)
        self.orientation = list(q)

    def fillBuffer(self, buffer):
        """Write the stored pose into the MiddlewareBuffer"""
        # Write position
        buffer.addFloat32(self.position[0])
        buffer.addFloat32(self.position[1])
        buffer.addFloat32(self.position[2])

        # Write orientation
        buffer.addFloat32(self.orientation[0])
        buffer.addFloat32(self.orientation[1])
        buffer.addFloat32(self.orientation[2])
        buffer.addFloat32(self.orientation[3])

    def loadPose(self, buffer: MiddlewareBuffer):
        self.position = [buffer.readNextFloat32() for _ in range(3)]
        self.orientation = [buffer.readNextFloat32() for _ in range(4)]

    def printPose(self):
        # Print in the original YAML format
        print("position:")
        print(f"  x: {self.position[0]}")
        print(f"  y: {self.position[1]}")
        print(f"  z: {self.position[2]}")
        print("orientation:")
        print(f"  x: {self.orientation[0]}")
        print(f"  y: {self.orientation[1]}")
        print(f"  z: {self.orientation[2]}")
        print(f"  w: {self.orientation[3]}")
        print("---")
