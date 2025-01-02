from PyQt5.QtGui import QColor, QImage
from PyQt5.QtCore import Qt

class BasicRender:
    def drawMain(self, painter):
        pass

class RectangleRender(BasicRender):
    def __init__(self, parent, data=None):
        self.parent = parent

        if 'color' in data:
            self.color = QColor(*data['color'])

        if data and 'image' in data:
            self.image = QImage(data["image"]).scaled(int(self.parent.length),
                                                      int(self.parent.width))
        else:
            self.image = None

    def drawRect(self, painter):
        painter.save()

        painter.setPen(Qt.black)
        painter.setBrush(self.color)

        painter.translate(int(self.parent.pos.x), int(self.parent.pos.y))
        painter.rotate(self.parent.angle)

        # Draw rectangle centered at origin
        painter.drawRect(int(-self.parent.length/2),
                         int(-self.parent.width/2),
                         int(self.parent.length),
                         int(self.parent.width))

        painter.restore()

    def drawImage(self, painter):
        """
        Draws the truck on the GUI.

        Args:
            painter (QPainter): the painter to draw with
        """
        # Set the color and draw the rectangle
        painter.save()

        painter.setPen(Qt.black)
        painter.setBrush(self.color)

        painter.translate(int(self.parent.pos.x), int(self.parent.pos.y))
        painter.rotate(self.parent.angle)
        # Draw rectangle centered at origin
        painter.translate(int(self.parent.wheelBase/2),0)
        painter.drawImage(int(-self.parent.length/2),
                         int(-self.parent.width/2),
                         self.image)

        painter.restore()

    def drawMain(self, painter):
        if self.image:
            self.drawImage(painter)
        else:
            self.drawRect(painter)

class SimpleVehicleRender:
    """
    A class representing a vehicle.
    """
    def __init__(self, parent, data=None):
        self.parent = parent
        self.color = QColor(255, 0, 0)
        self.axleWidth = data["axleWidth"]
        self.image = QImage(data["image"]).scaled(int(self.parent.length),
                                                  int(self.parent.width))

    def drawSquareVehicle(self, painter):
        """
        Draws the truck on the GUI.

        Args:
            painter (QPainter): the painter to draw with
        """
        # Set the color and draw the rectangle
        painter.save()

        painter.setPen(Qt.black)
        painter.setBrush(self.color)

        painter.translate(int(self.parent.pos.x), int(self.parent.pos.y))
        painter.rotate(self.parent.angle)
        # Draw rectangle centered at origin
        painter.translate(int(self.parent.wheelBase/2),0)
        painter.drawRect(int(-self.parent.length/2),
                         int(-self.parent.width/2),
                         int(self.parent.length),
                         int(self.parent.width))

        painter.restore()

    def drawImageVehicle(self, painter):
        """
        Draws the truck on the GUI.

        Args:
            painter (QPainter): the painter to draw with
        """
        # Set the color and draw the rectangle
        painter.save()

        painter.setPen(Qt.black)
        painter.setBrush(self.color)

        painter.translate(int(self.parent.pos.x), int(self.parent.pos.y))
        painter.rotate(self.parent.angle)
        # Draw rectangle centered at origin
        painter.translate(int(self.parent.wheelBase/2),0)
        painter.drawImage(int(-self.parent.length/2),
                         int(-self.parent.width/2),
                         self.image)
                         #sw=int(self.parent.length),
                         #sh=int(self.parent.width))

        painter.restore()

    def drawVehicle(self, painter):
        if self.image:
            self.drawImageVehicle(painter)
        else:
            self.drawSquareVehicle(painter)

    def drawMain(self, painter):
        self.drawVehicle(painter)

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

        painter.translate(int(self.parent.pos.x), int(self.parent.pos.y))
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

        #painter.save()
        #painter.rotate(self.parent.steeringAngle)
        #painter.drawLine(0,-1000,0,1000)
        #painter.restore()

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
        #painter.drawLine(0,-1000,0,1000)

        painter.drawRect(int(-self.parent.wheelDiameter/2),
                         int(-self.parent.wheelTread/2),
                         int(self.parent.wheelDiameter),
                         int(self.axleWidth))

        painter.drawRect(int(-self.parent.wheelDiameter/2),
                         int(self.parent.wheelTread/2-self.axleWidth),
                         int(self.parent.wheelDiameter),
                         int(self.axleWidth))
