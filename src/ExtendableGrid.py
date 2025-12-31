import numpy as np

INITIAL_WIDTH = 2000
INITIAL_HEIGHT = 2000

class ExtendableGrid:
    def __init__(self, initialValue):
        self.initialValue = initialValue
        self.grid = np.full(
            (INITIAL_HEIGHT, INITIAL_WIDTH),
            initialValue,
            dtype=int
        )

        self.yOffset = int(INITIAL_HEIGHT/2)
        self.xOffset = int(INITIAL_WIDTH/2)

    def getWidth(self):
        return self.grid.shape[1]

    def getHeight(self):
        return self.grid.shape[0]

    def getData(self):
        return self.grid.flatten(order="C").tolist()

    def setData(self, x: int, y: int, val: int):
        self.grid[y+self.yOffset, x+self.xOffset] = val
