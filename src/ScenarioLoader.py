import yaml

from SceneObjects import *
from VehicleRender import *
from Vehicle import Vehicle

class Alias:
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
            with open(self.aliasData['model'], "r") as file:
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
    def __init__(self, scenarioName):
        self.scenarioName = scenarioName
        with open(scenarioName, 'r') as file:
            self.data = yaml.safe_load(file)
        self.aliases = {}

        self.createAliases()
        self.loadingErrors = False

    def createAliases(self):
        if "aliases" not in self.data:
            return

        for aliasData in self.data["aliases"]:
            aliasObj = Alias(aliasData);
            if aliasObj.isValid():
                self.aliases[aliasObj.getName()] = aliasObj
            else:
                self.loadingError = True

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

        #In case of a loading error prevent saving that could corrupt the scenario
        if scenarioName == self.scenarioName and self.loadingErrors:
            print("Scenario contains loading errors, saving on the same file is not permitted!")
            return

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
