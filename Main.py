#!/usr/bin/env python3
import sys
import signal
import math
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QTimer

import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose

from VehicleRender import SimpleVehicleRender, WallRender
from SceneObjects import Wall
from Vehicle import Vehicle
from VehicleImporter import easyImport

DEFAULT_MODEL = "models/car.yaml"

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

class MainWindow(QMainWindow):
    """
    The GUI window for displaying the simualtor state
    """
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 800)
        self.angle = 0  # Initial rotation anglea
        self.setFocus()  # Enable keyboard focus

        model = DEFAULT_MODEL
        if len(sys.argv) > 1:
            model = sys.argv[1]

        self.truck, self.truckRender = easyImport(model)
        self.truck.x = 100.0
        self.truck.y = 100.0

        cmdVel = RosNode(self.truck, "vehicle1")
        cmdVel.start()

        wall1 = Wall((400,100), 0)
        wall2 = Wall((200,400), 90)
        self.sceneObjects = [WallRender(wall1), WallRender(wall2)]

        # Create and setup the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateRotation)
        self.timer.start(16)  # 16ms = ~60 FPS

    def updateRotation(self):
        self.update()    # Request repaint

    def paintEvent(self, event):
        """
        Main drawing function for the GUI
        """
        # pylint: disable=unused-argument
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.truck.tick(0.0016)
        self.truckRender.drawVehicle(painter)
        self.truckRender.drawAxles(painter)

        for obj in self.sceneObjects:
            obj.drawMain(painter)
            collision, vector = self.truck.checkCollision(obj.parent)
            if collision:
                self.truck.x -= vector[0]
                self.truck.y -= vector[1]

        painter.end()

    def keyPressEvent(self, event):
        """
        Handle GUI input events
        """
        if event.key() == Qt.Key_Up:
            self.truck.setThrottle(1)
        elif event.key() == Qt.Key_Down:
            self.truck.setThrottle(-1)
        elif event.key() == Qt.Key_Left:
            self.truck.setSteering(self.truck.getSteering()-1/16)
        elif event.key() == Qt.Key_Right:
            self.truck.setSteering(self.truck.getSteering()+1/16)

    def keyReleaseEvent(self, event):
        """
        Handle GUI input events
        """
        if event.key() == Qt.Key_Up:
            self.truck.setThrottle(0)
        elif event.key() == Qt.Key_Down:
            self.truck.setThrottle(0)
        elif event.key() == Qt.Key_Left:
            self.truck.setAngle(0)
        elif event.key() == Qt.Key_Right:
            self.truck.setAngle(0)

# Define a signal handler function
def handleSigint(signalReceived, frame):
    # pylint: disable=unused-argument
    print("Ctrl+C pressed. Exiting the application...")
    QApplication.quit()  # Gracefully quit the application

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handleSigint)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
