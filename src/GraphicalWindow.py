from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QScrollArea, QVBoxLayout
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QTimer

from SimEngine import RenderEngine

class DrawWidget(QWidget):
    def __init__(self, vehicle, renderEngine):
        super().__init__()
        self.setMinimumSize(2000,2000)

        self.vehicle = vehicle
        self.renderEngine = renderEngine

    def paintEvent(self, event):
        """
        Main drawing function for the GUI
        """
        # pylint: disable=unused-argument
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.renderEngine.draw(painter)

        painter.end()

class MainWindow(QMainWindow):
    """
    The GUI window for displaying the simualtor state
    """
    def __init__(self, vehicle):
        super().__init__()
        self.setGeometry(100, 100, 800, 800)
        self.angle = 0  # Initial rotation anglea

        self.vehicle = vehicle
        self.renderEngine = RenderEngine()

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")

        editAction = QAction("&Edit", self)
        editAction.setShortcut("Ctrl+E")
        editAction.triggered.connect(self.enableEditMode)
        fileMenu.addAction(editAction)

        # Create a central widget and set it
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # Create a layout for the central widget
        layout = QVBoxLayout(centralWidget)

        # Create a scroll area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)  # Allow the scroll area to resize

        # Create a widget to hold the content
        self.contentWidget = DrawWidget(vehicle, self.renderEngine)

        # Set the content widget to the scroll area
        self.scrollArea.setWidget(self.contentWidget)

        # Add the scroll area to the main layout
        layout.addWidget(self.scrollArea)

        # Create and setup the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateRotation)
        self.timer.start(16)  # 16ms = ~60 FPS

        # Set focus policy to ensure key events are received
        self.setFocus()  # Enable keyboard focus

    def getRenderEngine(self):
        return self.renderEngine

    def enableEditMode(self):
        print("Edit Mode Enabled")

    def updateRotation(self):
        self.contentWidget.update()    # Request repaint
        self.scrollArea.ensureVisible(int(self.vehicle.pos.x),
                                      int(self.vehicle.pos.y),
                                      300,
                                      300)

    def keyPressEvent(self, event):
        """
        Handle GUI input events
        """
        #if event.isAutoRepeat():
        #    return  # Ignore auto-repeat events

        if event.key() == Qt.Key_W:
            self.vehicle.setThrottle(1)
        elif event.key() == Qt.Key_S:
            self.vehicle.setThrottle(-1)
        elif event.key() == Qt.Key_A:
            self.vehicle.setSteering(self.vehicle.getSteering()-1/16)
        elif event.key() == Qt.Key_D:
            self.vehicle.setSteering(self.vehicle.getSteering()+1/16)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """
        Handle GUI input events
        """
        #if event.isAutoRepeat():
        #    return  # Ignore auto-repeat events

        if event.key() == Qt.Key_W:
            self.vehicle.setThrottle(0)
        elif event.key() == Qt.Key_S:
            self.vehicle.setThrottle(0)
        elif event.key() == Qt.Key_A:
            self.vehicle.setAngle(0)
        elif event.key() == Qt.Key_D:
            self.vehicle.setAngle(0)
        else:
            super().keyReleaseEvent(event)
