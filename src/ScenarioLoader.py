import yaml

from SceneObjects import *
from VehicleRender import *

class Alias:
    def __init__(self, classType, render):
        self.classType = classType
        self.render = render

    def genObject(self, loc, angle, dim):
        return globals()[self.classType](loc, angle, dim)

    def genRender(self, obj):
        return globals()[self.render](obj)

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
                    alias["render"])

    def instantiateScenario(self, simEngine, renderEngine):
        assert(simEngine is not None), "Simulation engine can't be None"
        assert('objects' in self.data), "Sceanrio file requires objects element"
        if 'static' in self.data['objects']:
            for obj in self.data['objects']['static']:
                print (obj)
                alias = self.aliases[obj['alias']]
                tmp = alias.genObject(obj['loc'], obj['angle'], obj['dim'])
                simEngine.registerStaticObject(tmp)
                if renderEngine is None:
                    continue
                renderEngine.registerObject(alias.genRender(tmp))
        #TODO:Load dynamic but how to bind the hotkeys????
