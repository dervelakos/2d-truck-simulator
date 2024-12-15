from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class SimpleVehicleRender:
    """
    A class representing a vehicle.
    """
    def __init__(self, parent, color=QColor(255,0,0)):
        self.parent = parent
        self.color = color
        self.axleWidth = 5

    def drawVehicle(self, painter):
        """
        Draws the truck on the GUI.

        Args:
            painter (QPainter): the painter to draw with
        """
        # Set the color and draw the rectangle
        painter.save()

        painter.setPen(Qt.black)
        painter.setBrush(self.color)

        painter.translate(int(self.parent.x), int(self.parent.y))
        painter.rotate(self.parent.angle)
        # Draw rectangle centered at origin
        painter.translate(int(self.parent.wheelBase/2),0)
        painter.drawRect(int(-self.parent.length/2),
                         int(-self.parent.width/2),
                         int(self.parent.length),
                         int(self.parent.width))

        painter.restore()

    def drawAxles(self, painter, color=Qt.black):
        """
        Draws the axles and wheels on the vehicle, this is considered a helper
        function

        Args:
            painter (QPainter): the painter to draw with
            color (float): color of the axles
        """
        painter.save()

        painter.setPen(Qt.black)
        painter.setBrush(color)

        painter.translate(int(self.parent.x), int(self.parent.y))
        painter.rotate(self.parent.angle)
        painter.translate(int(self.parent.wheelBase/2),0)

        painter.drawRect(int(self.parent.wheelBaseOffset-(self.parent.wheelBase/2)),
                         int(-self.axleWidth/2),
                         int(self.parent.wheelBase),
                         int(self.axleWidth))

        painter.translate(int(self.parent.wheelBaseOffset+(self.parent.wheelBase/2)),0)
        painter.drawRect(int(-self.axleWidth/2),
                         int(-self.parent.wheelTread/2),
                         int(self.axleWidth),
                         int(self.parent.wheelTread))
        self.drawFrontWheels(painter)
        painter.translate(-self.parent.wheelBase,0)

        #Draw rear axle components
        painter.drawRect(int(-self.axleWidth/2),
                         int(-self.parent.wheelTread/2),
                         int(self.axleWidth),
                         int(self.parent.wheelTread))
        self.drawRearWheels(painter)

        painter.restore()

    def drawFrontWheels(self, painter):
        '''
            Draws the front wheels. Must be called from the rear axle
            transformation to work correctly.
        '''

        painter.save()
        painter.rotate(self.parent.steeringAngle)
        painter.drawLine(0,-1000,0,1000)
        painter.restore()

        painter.save()
        painter.translate(0, -self.parent.wheelTread/2+self.axleWidth/2)
        painter.rotate(self.parent.steeringAngle)

        painter.drawRect(int(-self.parent.wheelDiameter/2),
                         int(-self.axleWidth/2),
                         int(self.parent.wheelDiameter),
                         int(self.axleWidth))
        painter.restore()

        painter.save()
        painter.translate(0, self.parent.wheelTread/2-self.axleWidth/2)
        painter.rotate(self.parent.steeringAngle)

        painter.drawRect(int(-self.parent.wheelDiameter/2),
                         int(-self.axleWidth/2),
                         int(self.parent.wheelDiameter),
                         int(self.axleWidth))
        painter.restore()

    def drawRearWheels(self, painter):
        '''
        Draws the rears wheels. Must be called from the rear axle
        transformation to work correctly.
        '''
        painter.drawLine(0,-1000,0,1000)

        painter.drawRect(int(-self.parent.wheelDiameter/2),
                         int(-self.parent.wheelTread/2),
                         int(self.parent.wheelDiameter),
                         int(self.axleWidth))

        painter.drawRect(int(-self.parent.wheelDiameter/2),
                         int(self.parent.wheelTread/2-self.axleWidth),
                         int(self.parent.wheelDiameter),
                         int(self.axleWidth))
