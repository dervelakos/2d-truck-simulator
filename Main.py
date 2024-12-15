#!/usr/bin/env python3
import sys
import math
import signal
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QTimer

from InertialModels import InertialModel1D
from VehicleRender import SimpleVehicleRender

class Vehicle:
    """
    A class representing a vehicle.
    """
    def __init__(self, initialPos, truckDimensions, axles=None):
        self.x = float(initialPos[0])
        self.y = float(initialPos[1])

        self.inModel = InertialModel1D(mass=100.0, friction=200.0)

        self.width = float(truckDimensions[1])
        self.length = float(truckDimensions[0])

        self.angle = 0

        self.linearSpeed = 1.0
        # Degrees per second
        self.angularSpeed = 90.0

        self.throttle = 0

        self.speed = 0

        self.maxSteeringAngle = 40.0
        self.steeringAngle = 40.0
        self.wheelDiameter = 20.0

        if axles:
            self.wheelBase = axles[0]
            self.wheelThread = axles[1]
            self.wheelBaseOffset = axles[2]
        else:
            self.wheelBase = self.length * 0.7
            self.wheelTread = self.width
            self.wheelBaseOffset = 0.0 #Shifts the wheels forward

    def setSteering(self, steering):
        self.steeringAngle = self.maxSteeringAngle * steering

    def getSteering(self):
        return self.steeringAngle / self.maxSteeringAngle

    def tick(self, dt):
        """
        Updates the state of vehicle (step) given a certain time difference.

        Args:
            dt (float): time difference from the last step in milliseconds.
        """
        self.inModel.applyForce(self.linearSpeed * self.throttle * dt *10000)
        self.inModel.update(dt)

        #Instantaneous Center of Rotation
        if abs(self.steeringAngle) > 0.000001:
            #no steering
            rads_steering = math.radians(self.steeringAngle)
            icr_y = self.wheelBase / math.tan(rads_steering)
            print("icr_y", icr_y)

            #theta_0 = math.atan2(0, icr_y)
            delta_theta = (self.inModel.getSpeed() * 10000 * dt) / icr_y  # Arc length formula

            rx = (icr_y * math.cos(delta_theta)) - icr_y
            ry = icr_y * math.sin(delta_theta)
            print("rx:", rx, ", ry: ",ry,", theta:",delta_theta )

            if abs(self.inModel.getSpeed()) > 0.000001:
                rads = math.radians(math.pi /2 - self.angle)
                self.y += rx * math.cos(rads) - ry * math.sin(rads)
                self.x += rx * math.sin(rads) + ry * math.cos(rads)
                self.angle += math.degrees(delta_theta)
                print("angle: ", self.angle, ", delta: ", math.degrees(delta_theta))
            #Imagine vehicle is always at (x,0) or (-x,0)
            #This would be a perfect turn
            #rads = math.radians(self.angle)
            #fx = 0.1 * math.cos(rads_steering) * self.throttle
            #fy = 0.1 * math.sin(rads_steering) * self.throttle

            #fx = self.inModel.getSpeed() * math.cos(rads_steering)
            #fy = self.inModel.getSpeed() * math.sin(rads_steering)
            #print("f:", fx, fy, self.steeringAngle)

            #rx = 0
            #ry = 1.5 * self.inModel.getSpeed()

            #if abs(self.inModel.getSpeed()) > 0.000001:
                #diff = math.atan2(fy, abs(icr_y)+fx)
                #diff = math.atan2(fy+self.wheelBase - ry, fx - rx)
                #print(math.degrees(math.pi/ 2 - diff))
                #self.angle += math.degrees(math.pi/ 2 - diff)

                #rx = 1.5 * math.cos(diff) * self.inModel.getSpeed()
                #ry = 1.5 * math.sin(diff) * self.inModel.getSpeed()
            #else:
                #diff = 0
                #rx = 0
                #ry = 0

            #rx = 1.5 * math.cos(diff) * self.throttle
            #ry = 1.5 * math.sin(diff) * self.throttle
            print(self.x, self.y, self.angle)
        else:
            ry = 1.5 * self.inModel.getSpeed()
            rx = 0

            rads = math.radians(math.pi /2 - self.angle)
            self.y += rx * math.cos(rads) - ry * math.sin(rads)
            self.x += rx * math.sin(rads) + ry * math.cos(rads)
        #print(self.inModel)

        #distance = self.linearSpeed * self.throttle * dt
        #rad = math.radians(self.angle)
        #delta_x = distance * math.cos(rad)
        #delta_y = distance * math.sin(rad)
        #self.x += delta_x
        #self.y += delta_y

    def getSpeed(self):
        return self.linearSpeed * self.throttle

    def setThrottle(self, throttle):
        self.throttle = throttle

    def setAngle(self, angle):
        self.angle += angle


class MainWindow(QMainWindow):
    """
    The GUI window for displaying the simualtor state
    """
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 800)
        self.angle = 0  # Initial rotation anglea
        self.setFocus()  # Enable keyboard focus

        self.truck = Vehicle([50.0,50.0], [130.0,80.0])
        self.truckRender = SimpleVehicleRender(self.truck)

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
