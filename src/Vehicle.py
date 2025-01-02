"""
Module containing a more complex scene object and thus seperated from the rest
"""

import math

from SceneObjects import SceneObject
from InertialModels import InertialModel1D
from Utils import Vector2D

class Vehicle(SceneObject):
    """
    A class representing a vehicle.
    """
    def __init__(self, initialPos, rotation, data):
        super().__init__(initialPos, rotation, data)

        self.inModel = InertialModel1D(mass=data["mass"],
                                       friction=data["friction"])

        print(data)
        self.width = data['width']
        self.length = data['length']

        self.linearSpeed = 1.0

        self.throttle = 0.0
        self.speed = 0.0

        self.maxSteeringAngle = data["steeringAngle"]
        self.steeringAngle = 0.0
        self.wheelDiameter = data["wheelDiameter"]

        if "axle" in data:
            self.wheelBase = data["axle"]["wheelBase"]
            self.wheelTread = data["axle"]["wheelTread"]
            self.wheelBaseOffset = data["axle"]["wheelBaseOffset"]
        else:
            self.wheelBase = self.length * 0.7
            self.wheelTread = self.width
            self.wheelBaseOffset = 0.0 #Shifts the wheels forward

        #self.boundOffset = [self.wheelBase/2, 0]
        self.boundOffset = Vector2D(self.wheelBase/2, 0)

    def setSteering(self, steering):
        steering = min(steering, 1)
        steering = max(steering, -1)

        self.steeringAngle = self.maxSteeringAngle * steering

    def getSteering(self):
        return self.steeringAngle / self.maxSteeringAngle

    def tick(self, dt):
        """
        Updates the state of vehicle (step) given a certain time difference.

        Args:
            dt (float): time difference from the last step in milliseconds.
        """
        self.inModel.applyForce(self.throttle * dt * 5000)
        self.inModel.update(dt)

        #Instantaneous Center of Rotation
        if abs(self.steeringAngle) > 0.000001:
            #no steering
            radSteering = math.radians(self.steeringAngle)
            icrY = self.wheelBase / math.tan(radSteering)
            #print("icrY", icrY)

            # Arc length formula
            deltaTheta = (self.inModel.getSpeed() * 100 * dt) / icrY
            rx = (icrY * math.cos(deltaTheta)) - icrY
            ry = icrY * math.sin(deltaTheta)

            if abs(self.inModel.getSpeed()) > 0.000001:
                rads = math.radians(math.pi /2 - self.angle)
                self.pos.y += rx * math.cos(rads) - ry * math.sin(rads)
                self.pos.x += rx * math.sin(rads) + ry * math.cos(rads)
                #self.pos += Vector2D(rx, ry).rotate(rads)
                self.angle += math.degrees(deltaTheta)

        else:
            ry = self.inModel.getSpeed() * 100 * dt
            rx = 0

            rads = math.radians(math.pi /2 - self.angle)
            self.pos.y += rx * math.cos(rads) - ry * math.sin(rads)
            self.pos.x += rx * math.sin(rads) + ry * math.cos(rads)
            #self.pos += Vector2D(rx, ry).rotate(rads)

    def getSpeed(self):
        return self.inModel.getSpeed()

    def setThrottle(self, throttle):
        self.throttle = throttle
