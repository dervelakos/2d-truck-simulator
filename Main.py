#!/usr/bin/env python3
import sys
import signal
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QTimer

from VehicleRender import SimpleVehicleRender
from Vehicle import Vehicle
from VehicleImporter import easyImport

DEFAULT_MODEL = "models/truck.yaml"

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
