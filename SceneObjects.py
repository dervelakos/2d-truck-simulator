import math

from Utils import Vector2D

class SceneObject:
    def __init__(self, initialPos, rotation):

        self.pos = Vector2D(initialPos[0], initialPos[1])
        self.angle = rotation

        #We support only rectanglular objects :P
        self.width = 0.0
        self.length = 0.0

        self.boundOffset = Vector2D(0.0, 0.0)

    def getCenter(self):
        rad = math.radians(self.angle)
        return self.pos + self.boundOffset.rotate(rad)

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
        rotatedOffsetX, rotatedOffsetY = self.boundOffset.rotate(rad).extract()

        print(self.pos)
        # Rotate corners around the center
        rotated_corners = []
        for corner in corners:
            rotated_x = corner[0] * math.cos(rad) - corner[1] * math.sin(rad)
            rotated_y = corner[0] * math.sin(rad) + corner[1] * math.cos(rad)
            rotated_corners.append((rotated_x + self.pos.x + rotatedOffsetX,
                                    rotated_y + self.pos.y + rotatedOffsetY))

        return rotated_corners

    def getAxes1(self):
        axes = []
        rads = math.radians(self.angle)
        axes.append((math.cos(rads), math.sin(rads)))
        axes.append((-math.sin(rads), math.cos(rads)))
        return axes

    def getAxis(self, p1, p2):
        edge = (p2[0] - p1[0], p2[1] - p1[1])
        axis = (-edge[1], edge[0])
        length = math.sqrt(axis[0]**2 + axis[1]**2)
        if length > 0:
            axis = (axis[0] / length, axis[1] / length)
        else:
            axis = (0,0)
        return axis

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
            if length > 0:
                axis = (axis[0] / length, axis[1] / length)
            else:
                axis = (0,0)
            axes.append(axis)

        return axes

    def project(self, axis, corners):
        """Calculates the min and max values after projecting the corners to the axis"""
        dots = []
        for corner in corners:
            dotProduct = (corner[0] * axis[0] + corner[1] * axis[1])
            dots.append(dotProduct)

        return min(dots), max(dots)

    def dotProduct(self, v1, v2):
        """
        Calculates the dot product of two vectors.
        """
        return v1[0] * v2[0] + v1[1] * v2[1]

    def getOverlapAmount(self, min1, max1, min2, max2):
        """
        Calculates the amount of overlap between two intervals.
        """
        # Ensure max > min for both intervals
        if max1 < min1:
            min1, max1 = max1, min1
        if max2 < min2:
            min2, max2 = max2, min1

        return max(0, min(max1, max2) - max(min1, min2))

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

        axes1 = self.getAxes()
        axes2 = sceneObject.getAxes()
        axes = axes1 + axes2

        minOverlapAmount = float('inf')
        minOverlapAxis = None

        # Iterate through all axes
        for axis in axes:
            # Project both rectangles onto the current axis
            min1, max1 = self.project(axis, rect1_corners)
            min2, max2 = sceneObject.project(axis, rect2_corners)

            # If there's a gap between the projections, they are not colliding
            if not (max1 >= min2 and max2 >= min1):
                return False, (0.0, 0.0)  # Separating axis found

            #Minimum Translation Vector (MTV)
            overlapAmount = self.getOverlapAmount(min1, max1, min2, max2)
            if overlapAmount < minOverlapAmount:
                minOverlapAmount = overlapAmount
                #minOverlapAxis = axis
                minOverlapAxis = Vector2D(axis[0], axis[1])

        center1 = self.getCenter()
        center2 = sceneObject.getCenter()
        directionVector = center2 - center1

        #if self.dotProduct(directionVector, minOverlapAxis) < 0:
        if directionVector.dot(minOverlapAxis) < 0:
            minOverlapAxis = -minOverlapAxis

        # No separating axis found, the rectangles are colliding, return
        # a pushback vector that resolves the collision
        return True, (minOverlapAxis * minOverlapAmount).extract()

    def __str__(self):
        return f"x:{self.x}, y: {self.y}, angle: {self.angle}, width: {self.width}, length: {self.length}"

class Wall(SceneObject):
    def __init__(self, initialPos, rotation, dimensions=[100.0, 10.0]):
        super().__init__(initialPos, rotation)

        self.width = dimensions[0]
        self.length = dimensions[1]
