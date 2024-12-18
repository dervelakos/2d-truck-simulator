import math

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
    axes = obj.getAxes()

    for axis in axes:
        min1, max1 = obj.project(axis, corners)
        #min2, max2 = project_ray((x, y), (dirX, dirY), (axisX, axisY))
        min2 = (x * axis[0] + y * axis[1])
        max2 = (x + 400000 * dirX) * axis[0] + (y + 400000 * dirY) * axis[1]
        #ray_proj_min, ray_proj_max = project(x, y, dirX, dirY, corners)
        #rect_proj_min, rect_proj_max = float('inf'), float('-inf')
        #Ray
        #min1, max1 = obj.project(axis, [(x, y)])
        #Rect
        #min2, max2 = obj.project(axis, [(x, y)])

        #for corner_x, corner_y in corners:
         #   proj = corner_x * axisX + corner_y * axisY
          #  rect_proj_min = min(rect_proj_min, proj)
           # rect_proj_max = max(rect_proj_max, proj)

        #if ray_proj_max < rect_proj_min or ray_proj_min > rect_proj_max:
        #    return None, None

        # Check if the projections overlap
        if max1 < min2 or min1 > max2:
            return None

        corners = obj.getCorners()
        min_distance = float('inf')

        for corner in corners:
            distance = math.sqrt((corner[0] - x) ** 2 + (corner[1] - y) ** 2)
            if distance < min_distance:
                min_distance = distance
        return min_distance


    try:
        return (100,100)
        hitX, hitY = project(x, y, dirX, dirY, corners)
        #hitX, hitY = obj.project((dirX, dirY), corners)
        return hitX, hitY
    except ZeroDivisionError:
        return None, None

def project(x, y, dirX, dirY, corners):
    min_proj, max_proj = float('inf'), float('-inf')
    for corner_x, corner_y in corners:
            proj = corner_x * dirX + corner_y * dirY
            min_proj = min(min_proj, proj)
            max_proj = max(max_proj, proj)
    return min_proj, max_proj

class Lidar:
    def __init__(self, numRays=360, rayAngleIncrement=1):
        self.numRays = numRays
        self.rayAngleIncrement = rayAngleIncrement

    def scan(self, x, y, angle, objects, ignoreObjects=[]):
        scanData = [0] * int(self.numRays / self.rayAngleIncrement)
        for i in range(self.numRays):
            rayAngleRad = math.radians(angle + i * self.rayAngleIncrement)

            #Ray Direction
            dirX = math.cos(rayAngleRad)
            dirY = math.sin(rayAngleRad)

            closestDist = float('inf')
            #closestObject = None

            for pobj in objects:
                obj = pobj.parent
                if obj in ignoreObjects:
                    continue

                #hitX, hitY = calculateIntersection(x, y, dirX, dirY, obj)
                dist = calculateIntersection(x, y, dirX, dirY, obj)
                if dist is None:
                    dist = float('inf')
                #if hitX is not None and hitY is not None:
                #    dist = math.sqrt((hitX - x)**2 + (hitY - y)**2)
                if dist < closestDist:
                    closestDist = dist
                        #closestObject = obj
            scanData[int(i/self.rayAngleIncrement)] = closestDist
            #scanData[i/self.rayAngleIncrement] = (closestDist, closestObject)
        return scanData


