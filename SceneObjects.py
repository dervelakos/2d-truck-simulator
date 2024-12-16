import math

class SceneObject:
    def __init__(self, initialPos, rotation):
        self.x = float(initialPos[0])
        self.y = float(initialPos[1])

        self.angle = rotation

        #We support only rectanglular objects :P
        self.width = 0.0
        self.length = 0.0

        self.boundOffset = [0.0, 0.0]

    def setAngle(self, angle):
        self.angle += angle

    def getAngle(self):
        return self.angle

    def getCorners(self):
        """
        Calculate the coordinates of the rectangle's four corners.

        Returns:
            list: A list of (x, y) tuples representing the corners.
        """
        # Half dimensions
        half_width = self.width / 2
        half_length = self.length / 2


        # Corners relative to the center (before rotation)
        corners = [
            (-half_length, -half_width),  # Bottom-left
            (half_length, -half_width),  # Bottom-right
            (half_length, half_width),   # Top-right
            (-half_length, half_width),  # Top-left
        ]

        # Convert angle from degrees to radians
        rad = math.radians(self.angle)
        rotatedOffsetX = self.boundOffset[0] * math.cos(rad) - self.boundOffset[1] * math.sin(rad)
        rotatedOffsetY = self.boundOffset[0] * math.sin(rad) + self.boundOffset[1] * math.cos(rad)

        # Rotate corners around the center
        rotated_corners = []
        print(self.boundOffset)
        for corner in corners:
            rotated_x = corner[0] * math.cos(rad) - corner[1] * math.sin(rad)
            rotated_y = corner[0] * math.sin(rad) + corner[1] * math.cos(rad)
            rotated_corners.append((rotated_x + self.x + rotatedOffsetX,
                                    rotated_y + self.y + rotatedOffsetY))

        return rotated_corners

    def getAxis(self, p1, p2):
        """Calculates the axis to perform the separating axis test"""
        return (p2[1]-p1[1], p1[0]-p2[0])

    def getAxes(self):
        """
        Get the axes to test for the Separating Axis Theorem (SAT).
        The axes are the perpendicular vectors to the edges of the rectangle.

        Returns:
            list: A list of (x, y) tuples representing the axes.
        """
        corners = self.getCorners()
        axes = []

        for i in range(len(corners)):
            # Get the edge vector
            p1 = corners[i]
            p2 = corners[(i + 1) % len(corners)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])

            # Get the perpendicular axis (normal to the edge)
            axis = (-edge[1], edge[0])
            # Normalize the axis
            length = math.sqrt(axis[0]**2 + axis[1]**2)
            axis = (axis[0] / length, axis[1] / length)
            axes.append(axis)

        return axes

    def project(self, axis, corners):
        """Calculates the min and max values after projecting the corners to the axis"""
        dots = []
        for corner in corners:
            dotProduct = (corner[0] * axis[0] + corner[1] * axis[1])
            dots.append(dotProduct)

        return min(dots), max(dots)

    def projectRectangle(rect, axis):
        """
        Project a rectangle onto a given axis.

        Args:
            rect (Rectangle): The rectangle to project.
            axis (tuple): The axis to project onto.

        Returns:
            tuple: The minimum and maximum values of the projection.
        """
        corners = rect.getCorners()
        projections = [(corner[0] * axis[0] + corner[1] * axis[1]) for corner in corners]
        return min(projections), max(projections)

    def checkCollision(self, sceneObject):
        """
        Check if two rectangles collide using the Separating Axis Theorem (SAT).

        Args:
            sceneObject (SceneObject): The other to check against.

        Returns:
            bool: True if the rectangles collide, False otherwise.
        """
        rect1_corners = self.getCorners()
        rect2_corners = sceneObject.getCorners()

        # Get all potential separating axes
        axes = [
            self.getAxis(rect1_corners[0], rect1_corners[1]),
            self.getAxis(rect1_corners[1], rect1_corners[2]),
            sceneObject.getAxis(rect2_corners[0], rect2_corners[1]),
            sceneObject.getAxis(rect2_corners[1], rect2_corners[2]),
        ]

        # Iterate through all axes
        for axis in axes:
            # Project both rectangles onto the current axis
            min1, max1 = self.project(axis, rect1_corners)
            min2, max2 = sceneObject.project(axis, rect2_corners)

            # If there's a gap between the projections, they are not colliding
            if max1 < min2 or max2 < min1:
                return False  # Separating axis found

        # No separating axis found, the rectangles are colliding
        return True

        # Get all axes to test (from both rectangles)
        axes1 = self.getAxes()
        axes2 = sceneObject.getAxes()
        axes = axes1 + axes2

        # Test each axis
        for axis in axes:
            # Project both rectangles onto the axis
            projection1 = self.projectRectangle(axis)
            projection2 = sceneObject.projectRectangle(axis)

            # Check for overlap
            if projection1[1] < projection2[0] or projection2[1] < projection1[0]:
                # No overlap on this axis, so no collision
                return False

        # No separating axis found, so the rectangles collide
        return True

    def __str__(self):
        return f"x:{self.x}, y: {self.y}, angle: {self.angle}, width: {self.width}, length: {self.length}"

class Wall(SceneObject):
    def __init__(self, initialPos, rotation, dimensions=[100.0, 10.0]):
        super().__init__(initialPos, rotation)

        self.width = dimensions[0]
        self.length = dimensions[1]
