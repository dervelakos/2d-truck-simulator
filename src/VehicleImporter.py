import yaml

from Vehicle import Vehicle
from VehicleRender import SimpleVehicleRender

class VehicleDescription:
    def __init__(self, descriptor):
        with open(descriptor, 'r') as file:
            self.data = yaml.safe_load(file)

        self.vehicle = None
        self.vehicleRender = None

    def getVehicle(self, initialPos=[0,0], rotation=0):
        if self.vehicle is None:
            self.vehicle = Vehicle(initialPos, rotation, data=self.data)
        return self.vehicle

    def getVehicleRender(self):
        if self.vehicleRender is None:
            self.vehicleRender = SimpleVehicleRender(self.getVehicle(),
                                                     data=self.data)
        return self.vehicleRender

def easyImport(descriptor):
    desc = VehicleDescription(descriptor)
    return desc.getVehicle(), desc.getVehicleRender()
