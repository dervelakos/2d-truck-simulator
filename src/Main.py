#!/usr/bin/env python3
import sys
import signal
import math
import datetime
import argparse

from PyQt5.QtWidgets import QApplication

from VehicleRender import SimpleVehicleRender, RectangleRender
from Vehicle import Vehicle
from VehicleImporter import easyImport
from Sensors import Lidar
from Utils import Vector2D
from SimEngine import SimEngine
from GraphicalWindow import MainWindow
from ScenarioLoader import ScenarioLoader

try:
    from RosNodes import RosNode
except ImportError as e:
    print(f"Module RosNodes could not be imported: {e}")

DEFAULT_MODEL = "models/car.yaml"
DEFAULT_SCENARIO = "scenarios/default.yaml"

simEngine = None
lidar = None
rosNode = None

# Define a signal handler function
def handleSigint(signalReceived, frame):
    # pylint: disable=unused-argument
    print("Ctrl+C pressed. Exiting the application...")
    QApplication.quit()  # Gracefully quit the application

    simEngine.stop()
    lidar.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handleSigint)

    parser = argparse.ArgumentParser(description="A 2d truck/vehicle simulator")
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO, help="The default map to load")
    parser.add_argument("--graphics", action="store_true", help="Start Qt5 window")
    parser.add_argument("--ros", action="store_true", help="Start ROS nodes (requires sourced ros)")
    parser.add_argument("model", type=str, nargs='?', default=DEFAULT_MODEL, help="Model of the vehicle")

    args = parser.parse_args()

    #Simulation Engine
    simEngine = SimEngine()

    scenario = ScenarioLoader(args.scenario)

    #Create Vehicle
    truck, truckRender = easyImport(args.model)
    truck.pos = Vector2D(100, 100)

    if args.graphics:
        app = QApplication(sys.argv)
        window = MainWindow(truck, scenario, simEngine)

    simEngine.registerDynamicObject(truck)
    if args.graphics:
        window.getRenderEngine().registerVehicle(truckRender)

    if args.ros:
        rosNode = RosNode(truck, "vehicle1")
    #Lidar
    lidar = Lidar(simEngine, truck, rosNode=rosNode)

    scenario.instantiateScenario(simEngine, window.getRenderEngine())

    simEngine.startThreaded()
    if rosNode:
        rosNode.start()
    lidar.startThreaded()

    if args.graphics:
        window.show()
        sys.exit(app.exec_())

    #Terminate
    lidar.wait()
    simEngine.wait()

