import math
import time
import threading

def lineLineIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
    # Line-line intersection formula
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # Lines are parallel or coincident

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        intersectionX = x1 + t * (x2 - x1)
        intersectionY = y1 + t * (y2 - y1)
        return (intersectionX, intersectionY)

    return None

def distanceBetweenPoints(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def projectRay(rayOrigin, rayDirection, axis):
    """Project a ray onto an axis."""
    # Normalize the ray direction
    length = math.sqrt(rayDirection[0]**2 + rayDirection[1]**2)
    normalizedDirection = (rayDirection[0] / length, rayDirection[1] / length)

    # Project the ray origin onto the axis
    dotProduct = rayOrigin[0] * axis[0] + rayOrigin[1] * axis[1]
    projectionOrigin = dotProduct

    # Project the ray direction onto the axis
    dotProduct = normalizedDirection[0] * axis[0] + normalizedDirection[1] * axis[1]
    projectionDirection = dotProduct

    # Return the projection range (min, max)
    if projectionDirection >= 0:
        # Ray extends infinitely in the positive direction
        return (projectionOrigin, float('inf'))

    # Ray extends infinitely in the negative direction
    return (float('-inf'), projectionOrigin)

def calculateIntersection(x, y, dirX, dirY, obj):
    corners = obj.getCorners()
    lidarEnd = (x + dirX, y + dirY)

    minDistance = float('inf')
    collisionPoint = None
    #axis1 = (-axis[1], axis[0])

    for i in range(4):
        edgeStart = corners[i]
        edgeEnd = corners[(i + 1) % 4]

        intersection = lineLineIntersection(
            x, y,
            lidarEnd[0], lidarEnd[1],
            edgeStart[0], edgeStart[1],
            edgeEnd[0], edgeEnd[1]
        )

        if intersection:
            dist = distanceBetweenPoints(x, y, intersection[0], intersection[1])
            if dist < minDistance and dist <= 1000: #maxLen
                minDistance = dist
                collisionPoint = intersection

    if collisionPoint:
        return minDistance
    return None

class Lidar:
    def __init__(self, simEngine, vehicle, rosNode=None,
                 numRays=360, rayAngleIncrement=1, interval=1/60):
        self.numRays = numRays
        self.rayAngleIncrement = rayAngleIncrement

        self.simEngine = simEngine
        self.vehicle = vehicle
        self.rosNode = rosNode

        self.thread = None
        self.interval = interval
        self.running = False

    def scan(self, x, y, angle, objects, ignoreObjects=[]):
        scanData = [0] * int(self.numRays / self.rayAngleIncrement)
        for i in range(self.numRays):
            rayAngleRad = math.radians(angle + i * self.rayAngleIncrement)

            #Ray Direction
            #1000 is the maximum length of the lidar
            dirX = math.cos(rayAngleRad) * 1000
            dirY = math.sin(rayAngleRad) * 1000

            closestDist = float('inf')
            #closestObject = None

            for obj in objects:
                if obj in ignoreObjects:
                    continue

                dist = calculateIntersection(x, y, dirX, dirY, obj)
                if dist is None:
                    dist = float('inf')
                if dist < closestDist:
                    closestDist = dist
                    #closestObject = obj
            scanData[int(i/self.rayAngleIncrement)] = closestDist
            #scanData[i/self.rayAngleIncrement] = (closestDist, closestObject)
        return scanData

    def run(self):
        while self.running:
            scanData = self.scan(self.vehicle.pos.x,
                                   self.vehicle.pos.y,
                                   self.vehicle.getAngle(),
                                   self.simEngine.getAllObjects(),
                                   [self.vehicle])

            if self.rosNode:
                scaledData = [x / 100 for x in scanData]
                self.rosNode.node.publishLidar(scaledData,
                                               self,
                                               self.vehicle.getAngle(),
                                               self.interval)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def wait(self):
        self.thread.join()

    def startThreaded(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
