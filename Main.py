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
        self.truck.x = 100.0
        self.truck.y = 100.0

        if useRos:
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


