"""
Module running all the physics of the simulation
"""
import threading
import time

from Utils import Vector2D

class SimEngine:
    """
    The physics engine
    """
    def __init__(self, interval=1.0/60):
        self.staticObjects = []
        self.dynamicObjects = []

        self.thread = None
        self.interval = interval
        self.running = False

    def registerStaticObject(self, obj):
        self.staticObjects.append(obj)

    def registerDynamicObject(self, obj):
        self.dynamicObjects.append(obj)

    def tickEngine(self, dt):
        """
        Main tick that updates all objects in the scenario
        """
        for obj in self.dynamicObjects:
            obj.tick(dt)

        for obj in self.dynamicObjects:
            for obj2 in self.staticObjects:
                collision, vector = obj.checkCollision(obj2)
                if collision:
                    obj.pos -= Vector2D(vector[0], vector[1])

            for obj2 in self.dynamicObjects:
                if obj == obj2:
                    continue
                collision, vector = obj.checkCollision(obj2)
                if collision:
                    obj.pos -= Vector2D(vector[0], vector[1])

    def getStaticObjects(self):
        return self.staticObjects

    def getDynamicObjects(self):
        return self.dynamicObjects

    def getAllObjects(self):
        return self.staticObjects + self.dynamicObjects

    def run(self):
        while self.running:
            self.tickEngine(self.interval)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def wait(self):
        self.thread.join()

    def startThreaded(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

class RenderEngine:
    """
    Render Engine that contains all the drawable objects
    """
    def __init__(self):
        self.objects = []

    def registerObject(self, obj):
        self.objects.append(obj)

    def draw(self, painter):
        """
        Method that will draw all the object on the canvas
        """
        for obj in self.objects:
            obj.drawMain(painter)
