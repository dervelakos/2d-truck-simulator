"""
Module handling all Qt5 and graphical interface functionality
"""
import math

from PyQt5.QtWidgets import (
        QMainWindow, QAction, QWidget,
        QScrollArea, QHBoxLayout, QListWidget)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import Qt, QTimer, QPoint

from SimEngine import RenderEngine

class UIController:
    """
    Class hanlding the control state machine for all graphical interfaces
    """
    def __init__(self, mainArea, simEngine, renderEngine, aliases):
        self.mainArea = mainArea
        self.simEngine = simEngine
        self.renderEngine = renderEngine
        self.aliases = aliases
        self.drawArea = None

        self.editMode = False
        self.selectedListObject = next(iter(self.aliases))
        print(self.selectedListObject)

    def toggleEditMode(self):
        self.editMode = not self.editMode
        self.mainArea.selectionList.setVisible(self.editMode)
        return self.editMode

    def selectListObject(self, item):
        self.selectedListObject = item.text()

    def createObject(self):
        """
        Creates and spawns a new object under the cursor
        """
        if not self.editMode:
            return

        p1 = self.drawArea.dragStartPosition
        p2 = self.drawArea.dragPosition

        delta = QPoint(p2 - p1)
        angle = math.degrees(math.atan2(delta.y(), delta.x()))

        length = math.hypot(delta.x(), delta.y())
        width = 10
        # Calculate the perpendicular vector for height
        # Rotate 90 degrees clockwise
        dx = width * math.sin(math.radians(angle))  # Change in x for height
        dy = -width * math.cos(math.radians(angle)) # Change in y for height

        # Calculate bottom corners
        x4, y4 = p2.x() - dx, p2.y() - dy  # bottom-right

        centerX = int((p1.x() + x4) / 2)
        centerY = int((p1.y() + y4) / 2)
        print (centerX, centerY, angle+90, length, width)

        if self.editMode:
            alias = self.aliases[self.selectedListObject]
            tmp = alias.genObject([centerX, centerY], angle)
            if tmp.isResizable():
                tmp.setDimensions(width, length)
            tmp.setAlias(alias)
            self.simEngine.registerStaticObject(tmp)
            self.renderEngine.registerObject(alias.genRender(tmp))

    def drawSelectionShadow(self, painter):
        """
        Draw a shadow of the object we will create
        """
        if (self.drawArea.dragStartPosition is None or
                self.drawArea.dragPosition is None):
            return

        p1 = self.drawArea.dragStartPosition
        p2 = self.drawArea.dragPosition

        delta = QPoint(p2 - p1)
        angle = math.degrees(math.atan2(delta.y(), delta.x()))

        length = math.hypot(delta.x(), delta.y())
        width = 10

        painter.save()

        painter.setPen(Qt.black)
        painter.setBrush(QColor(255, 0, 0, 64))

        painter.drawRect(int(p1.x()),
                         int(p1.y()),
                         int(delta.x()),
                         int(delta.y()))

        painter.restore()

        painter.save()
        painter.setPen(Qt.black)
        painter.setBrush(QColor(0, 255, 0, 64))
        painter.translate(int(p1.x()), int(p1.y()))
        painter.rotate(angle)
        painter.drawRect(0, 0, int(length), int(width))
        painter.restore()

        # Calculate the perpendicular vector for height
        # Rotate 90 degrees clockwise
        dx = width * math.sin(math.radians(angle))  # Change in x for height
        dy = -width * math.cos(math.radians(angle)) # Change in y for height

        # Calculate bottom corners
        x4, y4 = p2.x() - dx, p2.y() - dy  # bottom-right

        centerX = int((p1.x() + x4) / 2)
        centerY = int((p1.y() + y4) / 2)

        painter.drawEllipse(QPoint(centerX, centerY), 1, 1)

class DrawWidget(QWidget):
    """
    This is the canvas for drawing the scenario. Do not add Qt5 elements
    in here.
    """
    def __init__(self, vehicle, renderEngine, controller):
        super().__init__()
        self.setMinimumSize(2000,2000)

        self.vehicle = vehicle
        self.renderEngine = renderEngine

        self.dragging = False
        self.dragStartPosition = None
        self.dragPosition = None

        self.controller = controller

    def paintEvent(self, event):
        """
        Main drawing function for the GUI
        """
        # pylint: disable=unused-argument
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.renderEngine.draw(painter)

        self.controller.drawSelectionShadow(painter)

        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.dragPosition = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Handles mouse release events
        """
        if event.button() == Qt.LeftButton:
            print(self.controller)
            self.controller.createObject()
            self.dragging = False
            print(f"Start:{self.dragStartPosition}, End: {event.pos()}")

            self.dragStartPosition = None
            self.dragPosition = None

class MainWindow(QMainWindow):
    """
    The GUI window for displaying the simualtor state
    """
    def __init__(self, vehicle, scenario, simEngine):
        super().__init__()
        self.setGeometry(100, 100, 800, 800)

        self.vehicle = vehicle
        self.scenario = scenario
        self.simEngine = simEngine

        self.renderEngine = RenderEngine()

        #Pylint is right this class contains a lot of attributes I need to
        #refactor all theses classes (the upper ones above as well)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")

        editAction = QAction("&Edit", self)
        editAction.setShortcut("Ctrl+E")
        editAction.triggered.connect(self.enableEditMode)
        fileMenu.addAction(editAction)

        saveAction = QAction("&Save", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.saveScenario)
        fileMenu.addAction(saveAction)

        # Create a central widget and set it
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # Create a layout for the central widget
        layout = QHBoxLayout(centralWidget)

        # Create a scroll area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)  # Allow the scroll area to resize

        self.controller = UIController(self,
                                       self.simEngine,
                                       self.renderEngine,
                                       self.scenario.getAliases())

        # Create a widget to hold the content
        self.contentWidget = DrawWidget(vehicle, self.renderEngine, self.controller)

        # Set the content widget to the scroll area
        self.scrollArea.setWidget(self.contentWidget)

        # Add the scroll area to the main layout
        layout.addWidget(self.scrollArea)

        self.selectionList = QListWidget()

        for itemName in self.controller.aliases:
            self.selectionList.addItem(itemName)

        self.selectionList.itemClicked.connect(self.controller.selectListObject)
        self.selectionList.setFixedWidth(100)
        self.selectionList.setVisible(False)
        layout.addWidget(self.selectionList)


        # Create and setup the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateRotation)
        self.timer.start(16)  # 16ms = ~60 FPS

        # Set focus policy to ensure key events are received
        self.setFocus()  # Enable keyboard focus

        self.controller.drawArea = self.contentWidget

    def getRenderEngine(self):
        return self.renderEngine

    def enableEditMode(self):
        status = self.controller.toggleEditMode()
        print("Edit Mode Enabled", status)

    def saveScenario(self):
        print("Save Scenario")
        self.scenario.saveScenario(self.simEngine)

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
