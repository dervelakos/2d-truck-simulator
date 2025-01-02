"""
Common classes to be used by mutiliple modules
"""

import math

class Vector2D:
    """
    A class representing a two dimentional vector
    """
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def rotate(self, rad):
        return Vector2D(self.x * math.cos(rad) - self.y * math.sin(rad),
                        self.x * math.sin(rad) + self.y * math.cos(rad))

    def extract(self):
        return self.x, self.y

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def __eq__(self, other):
        if not isinstance(other, Vector2D):
            return False
        return (round(self.x, 13) == round(other.x, 13) and
               round(self.y, 13) == round(other.y, 13))

    def __str__(self):
        return f"({self.x}, {self.y})"
