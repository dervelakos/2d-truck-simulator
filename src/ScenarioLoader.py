import yaml

from SceneObjects import *
from VehicleRender import *
from Vehicle import Vehicle

class Alias:
    #TODO: This initialization is too redudant simplify it
    def __init__(self, classType, model, render, name):
        self.classType = classType
        self.model = model
        self.render = render
        self.name = name

        if self.model:
            with open(self.model, "r") as file:
                self.data = yaml.safe_load(file)
        else:
            self.data = None

    def genObject(self, loc, angle):
        if self.data:
            return globals()[self.classType](loc, angle, data=self.data)
        return globals()[self.classType](loc, angle)

    def genRender(self, obj):
        if self.data:
            return globals()[self.render](obj, data=self.data)
        return globals()[self.render](obj)

    def getName(self):
        return self.name

    def getDict(self):
        return {"type": self.classType,
                "model": self.model,
                "render": self.render,
                "name": self.name}

class ScenarioLoader:
    def __init__(self, scenarioName):
        self.scenarioName = scenarioName
        with open(scenarioName, 'r') as file:
            self.data = yaml.safe_load(file)
        self.aliases = {}

        self.createAliases()

    def createAliases(self):
        if "aliases" not in self.data:
            return

        for alias in self.data["aliases"]:
            if ("type" not in alias or
               "model" not in alias or
               "name" not in alias or
               "render" not in alias):
                   print("Could not read alias (missing type or name).")
                   continue
            self.aliases[alias['name']] = Alias(
                    alias["type"],
                    alias["model"],
                    alias["render"],
                    alias["name"])

    def getAliases(self):
        return self.aliases

    def getYamlAliasses(self):
        aliasses = []
        for aliasName in self.aliases:
            alias = self.aliases[aliasName]
            aliasses.append(alias.getDict())

        return aliasses

    def getYamlStaticObjects(self, simEngine):
        staticObjects = []

        for obj in simEngine.getStaticObjects():
            staticObjects.append(obj.toDict())

        return staticObjects

    def getYamlObjects(self, simEngine):
        objects = {}

        dynamicObjects = []

        objects["static"] = self.getYamlStaticObjects(simEngine)
        objects["dynamic"] = dynamicObjects

        return objects

    def saveScenario(self, simEngine):
        self.saveAsScenario(self.scenarioName, simEngine)

    def saveAsScenario(self, scenarioName, simEngine):
        d = {"aliases": self.getYamlAliasses(),
             "objects": self.getYamlObjects(simEngine)}
        with open(scenarioName, 'w') as file:
            yaml.dump(d, file, default_flow_style=False)

    def instantiateScenario(self, simEngine, renderEngine):
        assert(simEngine is not None), "Simulation engine can't be None"
        assert('objects' in self.data), "Sceanrio file requires objects element"
        if 'static' in self.data['objects']:
            for obj in self.data['objects']['static']:
                print (obj)
                alias = self.aliases[obj['alias']]
                tmp = alias.genObject(obj['loc'], obj['angle'])
                tmp.setDimensions(obj['dim'][0],obj['dim'][1])
                tmp.setAlias(alias)
                simEngine.registerStaticObject(tmp)
                if renderEngine is None:
                    continue
                renderEngine.registerObject(alias.genRender(tmp))
        #TODO:Load dynamic but how to bind the hotkeys????
