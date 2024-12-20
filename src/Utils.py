import math

class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

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
