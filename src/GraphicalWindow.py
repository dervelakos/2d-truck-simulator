from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QTimer

from SimEngine import RenderEngine

class MainWindow(QMainWindow):
    """
    The GUI window for displaying the simualtor state
    """
    def __init__(self, vehicle):
        super().__init__()
        self.setGeometry(100, 100, 800, 800)
        self.angle = 0  # Initial rotation anglea
        self.setFocus()  # Enable keyboard focus

        self.vehicle = vehicle
        self.renderEngine = RenderEngine()

        # Create and setup the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateRotation)
        self.timer.start(16)  # 16ms = ~60 FPS

    def getRenderEngine(self):
        return self.renderEngine

    def updateRotation(self):
        self.update()    # Request repaint

    def paintEvent(self, event):
        """
        Main drawing function for the GUI
        """
        # pylint: disable=unused-argument
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.renderEngine.draw(painter)

        painter.end()

    def keyPressEvent(self, event):
        """
        Handle GUI input events
        """
        if event.key() == Qt.Key_Up:
            self.vehicle.setThrottle(1)
        elif event.key() == Qt.Key_Down:
            self.vehicle.setThrottle(-1)
        elif event.key() == Qt.Key_Left:
            self.vehicle.setSteering(self.vehicle.getSteering()-1/16)
        elif event.key() == Qt.Key_Right:
            self.vehicle.setSteering(self.vehicle.getSteering()+1/16)

    def keyReleaseEvent(self, event):
        """
        Handle GUI input events
        """
        if event.key() == Qt.Key_Up:
            self.vehicle.setThrottle(0)
        elif event.key() == Qt.Key_Down:
            self.vehicle.setThrottle(0)
        elif event.key() == Qt.Key_Left:
            self.vehicle.setAngle(0)
        elif event.key() == Qt.Key_Right:
            self.vehicle.setAngle(0)
