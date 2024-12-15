import math

from InertialModels import InertialModel1D

class Vehicle:
    """
    A class representing a vehicle.
    """
    def __init__(self, initialPos, rotation, data=None):
        self.x = float(initialPos[0])
        self.y = float(initialPos[1])

        self.inModel = InertialModel1D(mass=data["mass"],
                                       friction=data["friction"])

        print(data)
        self.width = data['width']
        self.length = data['length']

        self.angle = rotation

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

    def setSteering(self, steering):
        self.steeringAngle = self.maxSteeringAngle * steering

    def getSteering(self):
        return self.steeringAngle / self.maxSteeringAngle

    def tick(self, dt):
        """
        Updates the state of vehicle (step) given a certain time difference.

        Args:
            dt (float): time difference from the last step in milliseconds.
        """
        self.inModel.applyForce(self.throttle * dt *10000)
        self.inModel.update(dt)

        #Instantaneous Center of Rotation
        if abs(self.steeringAngle) > 0.000001:
            #no steering
            rads_steering = math.radians(self.steeringAngle)
            icr_y = self.wheelBase / math.tan(rads_steering)
            print("icr_y", icr_y)

            #theta_0 = math.atan2(0, icr_y)
            delta_theta = (self.inModel.getSpeed() * 10000 * dt) / icr_y  # Arc length formula

            rx = (icr_y * math.cos(delta_theta)) - icr_y
            ry = icr_y * math.sin(delta_theta)
            print("rx:", rx, ", ry: ",ry,", theta:",delta_theta )

            if abs(self.inModel.getSpeed()) > 0.000001:
                rads = math.radians(math.pi /2 - self.angle)
                self.y += rx * math.cos(rads) - ry * math.sin(rads)
                self.x += rx * math.sin(rads) + ry * math.cos(rads)
                self.angle += math.degrees(delta_theta)
                print("angle: ", self.angle, ", delta: ", math.degrees(delta_theta))
            #Imagine vehicle is always at (x,0) or (-x,0)
            #This would be a perfect turn
            #rads = math.radians(self.angle)
            #fx = 0.1 * math.cos(rads_steering) * self.throttle
            #fy = 0.1 * math.sin(rads_steering) * self.throttle

            #fx = self.inModel.getSpeed() * math.cos(rads_steering)
            #fy = self.inModel.getSpeed() * math.sin(rads_steering)
            #print("f:", fx, fy, self.steeringAngle)

            #rx = 0
            #ry = 1.5 * self.inModel.getSpeed()

            #if abs(self.inModel.getSpeed()) > 0.000001:
                #diff = math.atan2(fy, abs(icr_y)+fx)
                #diff = math.atan2(fy+self.wheelBase - ry, fx - rx)
                #print(math.degrees(math.pi/ 2 - diff))
                #self.angle += math.degrees(math.pi/ 2 - diff)

                #rx = 1.5 * math.cos(diff) * self.inModel.getSpeed()
                #ry = 1.5 * math.sin(diff) * self.inModel.getSpeed()
            #else:
                #diff = 0
                #rx = 0
                #ry = 0

            #rx = 1.5 * math.cos(diff) * self.throttle
            #ry = 1.5 * math.sin(diff) * self.throttle
            print(self.x, self.y, self.angle)
        else:
            ry = 1.5 * self.inModel.getSpeed()
            rx = 0

            rads = math.radians(math.pi /2 - self.angle)
            self.y += rx * math.cos(rads) - ry * math.sin(rads)
            self.x += rx * math.sin(rads) + ry * math.cos(rads)
        #print(self.inModel)

        #distance = self.linearSpeed * self.throttle * dt
        #rad = math.radians(self.angle)
        #delta_x = distance * math.cos(rad)
        #delta_y = distance * math.sin(rad)
        #self.x += delta_x
        #self.y += delta_y

    def getSpeed(self):
        return self.inModel.getSpeed()

    def setThrottle(self, throttle):
        self.throttle = throttle

    def setAngle(self, angle):
        self.angle += angle
