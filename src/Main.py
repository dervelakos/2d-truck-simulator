#!/usr/bin/env python3
import sys
import signal
import math
import datetime
import argparse

from PyQt5.QtWidgets import QApplication

from VehicleRender import SimpleVehicleRender, RectangleRender
from SceneObjects import Wall
from Vehicle import Vehicle
from VehicleImporter import easyImport
from Sensors import Lidar
from Utils import Vector2D
from SimEngine import SimEngine
from GraphicalWindow import MainWindow

try:
    from RosNodes import RosNode
except ImportError as e:
    print(f"Module RosNodes could not be imported: {e}")

DEFAULT_MODEL = "models/car.yaml"

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
    parser.add_argument("--graphics", action="store_true", help="Start Qt5 window")
    parser.add_argument("--ros", action="store_true", help="Start ROS nodes (requires sourced ros)")
    parser.add_argument("model", type=str, nargs='?', default=DEFAULT_MODEL, help="Model of the vehicle")

    args = parser.parse_args()

    #Create Vehicle
    truck, truckRender = easyImport(args.model)
    truck.pos = Vector2D(100, 100)

    if args.graphics:
        app = QApplication(sys.argv)
        window = MainWindow(truck)

    #Simulation Engine
    simEngine = SimEngine()
    simEngine.registerDynamicObject(truck)
    if args.graphics:
        window.getRenderEngine().registerVehicle(truckRender)

    if args.ros:
        rosNode = RosNode(truck, "vehicle1")
    #Lidar
    lidar = Lidar(simEngine, truck, rosNode=rosNode)

    #TODO: I need a scanario loader
    walls = []
    walls.append(Wall((400,100), 0))
    walls.append(Wall((200,400), 90))

    walls.append(Wall((400,0), 90, [800,10]))
    walls.append(Wall((400,800), 90, [800,10]))
    walls.append(Wall((0,400), 0, [800,10]))
    walls.append(Wall((800,400), 0, [800,10]))

    for wall in walls:
        simEngine.registerStaticObject(wall)
        if args.graphics:
            window.getRenderEngine().registerObject(RectangleRender(wall))

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

