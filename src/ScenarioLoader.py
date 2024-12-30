import yaml

from SceneObjects import *
from VehicleRender import *

class Alias:
    def __init__(self, classType, render, name):
        self.classType = classType
        self.render = render
        self.name = name

    def genObject(self, loc, angle, dim):
        return globals()[self.classType](loc, angle, dim)

    def genRender(self, obj):
        return globals()[self.render](obj)

    def getName(self):
        return self.name

    def getDict(self):
        return {"type": self.classType,
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
               "name" not in alias or
               "render" not in alias):
                   print("Could not read alias (missing type or name).")
                   continue
            self.aliases[alias['name']] = Alias(
                    alias["type"],
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
                tmp = alias.genObject(obj['loc'], obj['angle'], obj['dim'])
                tmp.setAlias(alias)
                simEngine.registerStaticObject(tmp)
                if renderEngine is None:
                    continue
                renderEngine.registerObject(alias.genRender(tmp))
        #TODO:Load dynamic but how to bind the hotkeys????
