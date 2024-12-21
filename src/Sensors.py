import math
import time
import threading

def line_line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    # Line-line intersection formula
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # Lines are parallel or coincident

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        intersection_x = x1 + t * (x2 - x1)
        intersection_y = y1 + t * (y2 - y1)
        return (intersection_x, intersection_y)

    return None

def distance_between_points(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def project_ray(ray_origin, ray_direction, axis):
    """Project a ray onto an axis."""
    # Normalize the ray direction
    length = math.sqrt(ray_direction[0]**2 + ray_direction[1]**2)
    normalized_direction = (ray_direction[0] / length, ray_direction[1] / length)

    # Project the ray origin onto the axis
    dot_product = ray_origin[0] * axis[0] + ray_origin[1] * axis[1]
    projection_origin = dot_product

    # Project the ray direction onto the axis
    dot_product = normalized_direction[0] * axis[0] + normalized_direction[1] * axis[1]
    projection_direction = dot_product

    # Return the projection range (min, max)
    if projection_direction >= 0:
        return (projection_origin, float('inf'))  # Ray extends infinitely in the positive direction
    else:
        return (float('-inf'), projection_origin)  # Ray extends infinitely in the negative direction

def calculateIntersection(x, y, dirX, dirY, obj):
    corners = obj.getCorners()
    lidar_end = (x + dirX, y + dirY)

    min_distance = float('inf')
    collision_point = None
    #axis1 = (-axis[1], axis[0])

    for i in range(4):
        edge_start = corners[i]
        edge_end = corners[(i + 1) % 4]

        #edgeX = end[0] - start[0]
        #edgeY = end[1] - start[1]

        intersection = line_line_intersection(
            x, y,
            lidar_end[0], lidar_end[1],
            edge_start[0], edge_start[1],
            edge_end[0], edge_end[1]
        )

        if intersection:
            dist = distance_between_points(x, y, intersection[0], intersection[1])
            if dist < min_distance and dist <= 1000: #maxLen
                min_distance = dist
                collision_point = intersection

    if collision_point:
        return min_distance
    else:
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
