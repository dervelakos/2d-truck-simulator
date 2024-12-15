import math

class InertialModel1D:
    """
    A 2D inertial model representing an object with speed, angle, position, and
    the ability to apply force.

    Attributes:
        speed (float): Current speed of the object.
        mass (float): Mass of the object (affects inertia).
        friction (float): Friction coefficient (reduces speed over time).
    """

    def __init__(self, speed=0.0, mass=1.0, friction=0.05):
        """
        Initializes the InertialModel2D.

        Args:
            speed (float): Initial speed.
            mass (float): Mass of the object.
            friction (float): Friction coefficient (0.0 - 1.0, where 0.0 is no
                              friction and 1.0 is high friction).
        """
        self.speed = speed
        self.mass = mass
        self.friction = friction

    def applyForce(self, force):
        """
        Applies a force to the object, affecting its speed and direction.

        Args:
            force (float): Magnitude of the force.
        """
        # Update velocity
        self.speed += force / self.mass

    def setFriction(self, friction):
        self.friction = friction

    def update(self, dt=0.1):
        """
        Updates the object's position and speed based on its current state and
        applied forces. Includes friction to slow down the object over time.

        Args:
            dt (float): Time step (in seconds).
        """
        # Apply friction
        self.speed *= (1 - self.friction * dt)

        # Handle very low speed to prevent jittering
        if -0.001 < self.speed < 0.001:
            self.speed = 0

    def getSpeed(self):
        return self.speed

    def __str__(self):
        return f"Speed: {self.speed:.2f}"

class InertialModel2D:
    """
    A 2D inertial model representing an object with speed, angle, position, and
    the ability to apply force.

    Attributes:
        x (float): x-coordinate of the object's position.
        y (float): y-coordinate of the object's position.
        speed (float): Current speed of the object.
        angle (float): Current angle of the object (in radians, 0 = right, pi/2 = up, etc.).
        mass (float): Mass of the object (affects inertia).
        friction (float): Friction coefficient (reduces speed over time).
        vx (float): Velocity in the x-direction.
        vy (float): Velocity in the y-direction.
    """

    def __init__(self, x=0.0, y=0.0, speed=0.0, angle=0.0, mass=1.0, friction=0.05):
        """
        Initializes the InertialModel2D.

        Args:
            x (float): Initial x-coordinate.
            y (float): Initial y-coordinate.
            speed (float): Initial speed.
            angle (float): Initial angle (in radians).
            mass (float): Mass of the object.
            friction (float): Friction coefficient (0.0 - 1.0, where 0.0 is no
                              friction and 1.0 is high friction).
        """
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.mass = mass
        self.friction = friction
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

    def applyForce(self, force, forceAngle):
        """
        Applies a force to the object, affecting its speed and direction.

        Args:
            force (float): Magnitude of the force.
            force_angle (float): Angle of the force (in radians).
        """
        # Resolve force into x and y components
        fx = force * math.cos(forceAngle)
        fy = force * math.sin(forceAngle)

        # Calculate acceleration
        ax = fx / self.mass
        ay = fy / self.mass

        # Update velocity
        self.vx += ax
        self.vy += ay

        # Update speed and angle based on new velocity
        self.speed = math.sqrt(self.vx**2 + self.vy**2)
        self.angle = math.atan2(self.vy, self.vx)

    def update(self, dt=0.1):
        """
        Updates the object's position and speed based on its current state and applied forces.
        Includes friction to slow down the object over time.

        Args:
            dt (float): Time step (in seconds).
        """
        # Apply friction
        self.vx *= (1 - self.friction * dt)
        self.vy *= (1 - self.friction * dt)

        # Update speed and angle based on new velocity after friction
        self.speed = math.sqrt(self.vx**2 + self.vy**2)

        # Handle very low speed to prevent jittering
        if self.speed < 0.001:
            self.speed = 0
            self.vx = 0
            self.vy = 0

        if self.speed != 0: #avoid errors when speed is exactly 0
            self.angle = math.atan2(self.vy, self.vx)


        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

    def __str__(self):
        return f"Position: ({self.x:.2f}, {self.y:.2f}), Speed: {self.speed:.2f}, Angle: {math.degrees(self.angle):.2f}°"
