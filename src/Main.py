#!/usr/bin/env python3
import sys
import signal
import math
import datetime
import argparse
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QTimer

from VehicleRender import SimpleVehicleRender, WallRender
from SceneObjects import Wall
from Vehicle import Vehicle
from VehicleImporter import easyImport
from Sensors import Lidar
from Utils import Vector2D
from SimEngine import SimEngine, RenderEngine

try:
    from RosNodes import RosNode
except ImportError as e:
    print(f"Module RosNodes could not be imported: {e}")

DEFAULT_MODEL = "models/car.yaml"

class MainWindow(QMainWindow):
    """
    The GUI window for displaying the simualtor state
    """
    def __init__(self, model, useRos=False):
        super().__init__()
        self.setGeometry(100, 100, 800, 800)
        self.angle = 0  # Initial rotation anglea
        self.setFocus()  # Enable keyboard focus

        self.truck, self.truckRender = easyImport(model)
        self.truck.pos = Vector2D(100, 100)

        self.simEngine = SimEngine()
        self.renderEngine = RenderEngine()
        self.simEngine.registerDynamicObject(self.truck)
        self.renderEngine.registerVehicle(self.truckRender)

        self.lidar = Lidar()

        if useRos:
            self.rosNode = RosNode(self.truck, "vehicle1")
            self.rosNode.start()
        else:
            self.rosNode = None

        wall1 = Wall((400,100), 0)
        self.simEngine.registerStaticObject(wall1)
        self.renderEngine.registerObject(WallRender(wall1))
        wall2 = Wall((200,400), 90)
        self.simEngine.registerStaticObject(wall2)
        self.renderEngine.registerObject(WallRender(wall2))

        wall3 = Wall((400,0), 90, [800,10])
        self.simEngine.registerStaticObject(wall3)
        self.renderEngine.registerObject(WallRender(wall3))
        wall4 = Wall((400,800), 90, [800,10])
        self.simEngine.registerStaticObject(wall4)
        self.renderEngine.registerObject(WallRender(wall4))
        wall5 = Wall((0,400), 0, [800,10])
        self.simEngine.registerStaticObject(wall5)
        self.renderEngine.registerObject(WallRender(wall5))
        wall6 = Wall((800,400), 0, [800,10])
        self.simEngine.registerStaticObject(wall6)
        self.renderEngine.registerObject(WallRender(wall6))

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

        dt = 0.0016

        self.simEngine.tickEngine(dt)
        self.renderEngine.draw(painter)

        scanData = self.lidar.scan(self.truck.pos.x,
                                   self.truck.pos.y,
                                   self.truck.angle,
                                   self.simEngine.getAllObjects(),
                                   [self.truck])

        if self.rosNode:
            scaledData = [x / 100 for x in scanData]
            self.rosNode.node.publishLidar(scaledData, self.lidar, self.truck.angle, dt)

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

    parser = argparse.ArgumentParser(description="A 2d truck/vehicle simulator")
    parser.add_argument("--graphics", action="store_true", help="Start Qt5 window")
    parser.add_argument("--ros", action="store_true", help="Start ROS nodes (requires sourced ros)")
    parser.add_argument("model", type=str, nargs='?', default=DEFAULT_MODEL, help="Model of the vehicle")

    args = parser.parse_args()

    if args.graphics:
        app = QApplication(sys.argv)
        window = MainWindow(args.model, args.ros)
        window.show()
        sys.exit(app.exec_())
    else:
        print("Not implemented yet.")


