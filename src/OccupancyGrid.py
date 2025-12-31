import numpy as np
import math

from Bresenham import bresenham
from Utils import Point2D
from CommMsgs import PoseMsg, LidarMsg

GRID_FREE = 0
GRID_BLOCKED = 100
GRID_UNKNOWN = -1

INITIAL_WIDTH = 2000
INITIAL_HEIGHT = 2000

def polar_to_grid_cell(angle: float, distance: float, cell_size: float, origin: Point2D):
    """
    angle: radians
    distance: meters
    cell_size: meters per cell
    origin_x, origin_y: robot position in grid cells
    """

    if distance == float("inf"):
        return Point2D()

    x = distance * math.cos(angle)
    y = distance * math.sin(angle)

    cell_x = int(origin.x) + int(x / cell_size)
    cell_y = int(origin.y) + int(y / cell_size)

    return Point2D(cell_x, cell_y)

def compute_padding(grid_shape, origin, new_cells):
    """
    Compute padding needed to fit new cells into a grid, avoiding repeated over-padding for negatives.

    Parameters
    ----------
    grid_shape : tuple (height, width)
        Current shape of the grid
    origin : tuple (origin_y, origin_x)
        Robot/reference position in the grid (row, col)
    new_cells : list of (x, y)
        List of new cell coordinates (column=x, row=y)

    Returns
    -------
    pad : tuple
        Format ((pad_bottom, pad_top), (pad_left, pad_right))
        Can be used directly with np.pad
    need_pad : bool
        True if any padding is needed
    new_origin : tuple
        The origin position after applying padding
    """

    height, width = grid_shape
    origin_y, origin_x = origin

    if not new_cells:
        return ((0, 0), (0, 0)), False, origin

    xs = [x for x, y in new_cells]
    ys = [y for x, y in new_cells]

    # Compute absolute min/max coordinates in grid space
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)

    # Compute padding needed
    pad_left   = max(0, - origin_x - min_x)
    pad_right  = max(0, max_x - (width - origin_x - 2))
    pad_bottom = max(0, - origin_y - min_y)
    pad_top    = max(0, max_y - (height - origin_y - 2))

    pad = ((pad_bottom, pad_top), (pad_left, pad_right))
    need_pad = any(p > 0 for pair in pad for p in pair)

    # New origin after padding
    new_origin_y = origin_y + pad_bottom -1
    new_origin_x = origin_x + pad_left - 1
    new_origin = (new_origin_y, new_origin_x)

    return pad, need_pad, new_origin

class OccupancyGrid:
    def __init__(self, resolution):
        self.resolution = resolution
        self.grid = np.full((INITIAL_WIDTH, INITIAL_HEIGHT), GRID_UNKNOWN, dtype=int)
        self.width = INITIAL_WIDTH
        self.height = INITIAL_HEIGHT
        self.grid_origin = Point2D(1000,1000)
        self.initPose = None
        self.deltaPoint = Point2D(0,0)

    def getWidth(self):
        #return self.width
        return self.grid.shape[1]

    def getHeight(self):
        #return self.height
        return self.grid.shape[0]

    def getData(self):
        return self.grid.flatten(order="C").tolist()

    def getResolution(self):
        return float(self.resolution)

    def getOrigin(self):
        return (-self.grid_origin.x+self.deltaPoint.x)*self.resolution, (-self.grid_origin.y+self.deltaPoint.y)*self.resolution

    def resize(self, pad):
        if all(p == 0 for pair in pad for p in pair):
            return
        #self.width += abs(pad_width[1][0]) + abs(pad_width[1][1])
        #self.height += abs(pad_width[0][0]) + abs(pad_width[0][1])
        self.grid = np.pad(
            self.grid,
            pad_width = pad,
            mode = "constant",
            constant_values = GRID_UNKNOWN
        )

    def processScan(self, msg, msg1):
        origin = Point2D(0, 0)

        if self.initPose is None:
            self.initPose = Point2D(int(msg1.position[1]*self.resolution), int(msg1.position[0]/self.resolution))

        curr = Point2D(int(msg1.position[1]/self.resolution), int(msg1.position[0]/self.resolution))
        deltaPoint = curr - self.initPose
        print(curr, deltaPoint)
        self.deltaPoint = deltaPoint

        angle = msg.angle_min
        for dist in msg.ranges:
            cellPoint = polar_to_grid_cell(angle, dist, self.resolution, -deltaPoint)
            if not cellPoint.isValid():
                continue
            #print(dist, angle, cellPoint)
            #cells = bresenham(origin, cellPoint)
            #print("Bres:",deltaPoint, cellPoint)
            cells = bresenham(-deltaPoint, cellPoint)
            #pad, need_pad, new_origin = compute_padding(self.grid.shape, self.grid_origin, cells)
            #print(cells)
            #print(self.grid.shape, pad, need_pad, new_origin)
            #if need_pad:
                #self.resize(pad)
                #self.grid_origin = new_origin
            #print(cellPoint, self.grid_origin)
            #print(cells)
            for cell in cells:
                self.grid[cell.y+self.grid_origin.y][cell.x+self.grid_origin.x] = 0
            self.grid[cellPoint.y+self.grid_origin.y][cellPoint.x+self.grid_origin.x] = GRID_BLOCKED
            angle += msg.angle_increment
        print(f"Shape:{self.grid.shape}, Orig:{self.grid_origin}")
