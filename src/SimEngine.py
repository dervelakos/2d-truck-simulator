from Utils import Vector2D
class SimEngine:
    def __init__(self):
        self.staticObjects = []
        self.dynamicObjects = []

    def registerStaticObject(self, obj):
        self.staticObjects.append(obj)

    def registerDynamicObject(self, obj):
        self.dynamicObjects.append(obj)

    def tickEngine(self, dt):
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

    def getAllObjects(self):
        return self.staticObjects + self.dynamicObjects

class RenderEngine:
    def __init__(self):
        self.objects = []
        self.vehicles = []

    def registerObject(self, obj):
        self.objects.append(obj)

    def registerVehicle(self, obj):
        self.vehicles.append(obj)

    def draw(self, painter):
        for obj in self.objects:
            obj.drawMain(painter)

        for obj in self.vehicles:
            obj.drawVehicle(painter)
            obj.drawAxles(painter)
