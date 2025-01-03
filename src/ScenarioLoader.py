"""
This module contains all the necessary fuctionality to load a scenario from a
yaml file
"""

import yaml
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from SceneObjects import *
from VehicleRender import *
from Vehicle import Vehicle # pylint: disable=unused-import

class Alias:
    """
    This class describes a object to be reused when saving and loading a
    scenario.
    """
    def __init__(self, aliasData):
        self.aliasData = aliasData
        self.data = None

    def isValid(self):
        """
        Minimum viable configuration
        """
        if 'type' not in self.aliasData:
            return False
        if 'name' not in self.aliasData:
            return False
        if 'render' not in self.aliasData:
            return False
        if 'model' not in self.aliasData:
            return False
        return True

    def getModelData(self):
        if self.data is None:
            with open(self.aliasData['model'], "r", encoding="utf-8") as file:
                self.data = yaml.safe_load(file)
        return self.data

    def genObject(self, loc, angle):
        modelData = self.getModelData()
        if modelData:
            return globals()[self.aliasData['type']](loc, angle, data=modelData)
        return globals()[self.aliasData['type']](loc, angle)

    def genRender(self, obj):
        modelData = self.getModelData()
        if modelData:
            return globals()[self.aliasData['render']](obj, data=modelData)
        return globals()[self.aliasData['render']](obj)

    def getName(self):
        return self.aliasData['name']

    def getDict(self):
        return self.aliasData

class ScenarioLoader:
    """
    Class for loading a scenario from a yaml file
    """
    def __init__(self, scenarioName):
        self.scenarioName = scenarioName
        with open(scenarioName, 'r', encoding="utf-8") as file:
            self.data = yaml.safe_load(file)
        self.aliases = {}

        self.createAliases()
        self.loadingErrors = False

        self.namedObjects = {}

    def createAliases(self):
        """
        Parse all the alises from the yaml file
        """
        if "aliases" not in self.data:
            return

        for aliasData in self.data["aliases"]:
            aliasObj = Alias(aliasData)
            if aliasObj.isValid():
                self.aliases[aliasObj.getName()] = aliasObj
            else:
                self.loadingError = True

    def getAliases(self):
        return self.aliases

    def getNamedObject(self, name):
        if name in self.namedObjects:
            return self.namedObjects[name]
        return None

    def getYamlAliasses(self):
        """
        Generate yaml structure for all the aliases
        """
        aliasses = []
        for alias, _ in self.aliases.items():
            aliasses.append(alias.getDict())

        return aliasses

    def getYamlStaticObjects(self, simEngine):
        """
        Generate yaml structure for all the static objects
        """
        staticObjects = []

        for obj in simEngine.getStaticObjects():
            staticObjects.append(obj.toDict())

        return staticObjects

    def getYamlObjects(self, simEngine):
        """
        Generate yaml structure for all the objects in the scenario
        """
        objects = {}

        dynamicObjects = []

        objects["static"] = self.getYamlStaticObjects(simEngine)
        objects["dynamic"] = dynamicObjects

        return objects

    def saveScenario(self, simEngine):
        self.saveAsScenario(self.scenarioName, simEngine)

    def saveAsScenario(self, scenarioName, simEngine):
        """
        Save the scenario as it currently is
        """
        d = {"aliases": self.getYamlAliasses(),
             "objects": self.getYamlObjects(simEngine)}

        #In case of a loading error prevent saving that could corrupt the scenario
        if scenarioName == self.scenarioName and self.loadingErrors:
            print("Scenario contains loading errors, saving on the same file is not permitted!")
            return

        with open(scenarioName, 'w', encoding="utf-8") as file:
            yaml.dump(d, file, default_flow_style=False)

    def loadObject(self, obj):
        alias = self.aliases[obj['alias']]
        tmp = alias.genObject(obj['loc'], obj['angle'])
        tmp.setDimensions(obj['dim'][0],obj['dim'][1])
        tmp.setAlias(alias)

        if 'name' in obj:
            self.namedObjects[obj['name']]=tmp

        return tmp, alias

    def instantiateScenario(self, simEngine, renderEngine):
        """
        Loads all the objects of the scenario into the engines
        """
        assert(simEngine is not None), "Simulation engine can't be None"
        assert('objects' in self.data), "Sceanrio file requires objects element"
        if 'static' in self.data['objects']:
            for obj in self.data['objects']['static']:
                print (obj)
                tmp, alias = self.loadObject(obj)
                simEngine.registerStaticObject(tmp)
                if renderEngine is None:
                    continue
                renderEngine.registerObject(alias.genRender(tmp))
        if 'dynamic' in self.data['objects']:
            for obj in self.data['objects']['dynamic']:
                print (obj)
                tmp, alias = self.loadObject(obj)
                simEngine.registerDynamicObject(tmp)
                if renderEngine is None:
                    continue
                renderEngine.registerObject(alias.genRender(tmp))
        #TODO:Load dynamic but how to bind the hotkeys????
