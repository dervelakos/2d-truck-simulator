from Middleware import OutputDataStream
from MiddlewareBuffer import MiddlewareBuffer
from CommMsgs import PoseMsg, LidarMsg

import threading
import time

class LidarPublisher:
    def __init__(self, lidar, stream):
        self.lidar = lidar
        self.lidarStream = stream

    def publish(self):
        lidarBuf = self.lidarStream.getBuffer(2892)
        lidarMsg = LidarMsg()
        vehicle = self.lidar.vehicle
        scanData = self.lidar.scan(vehicle.pos.x,
                               vehicle.pos.y,
                               vehicle.getAngle(),
                               self.lidar.simEngine.getAllObjects(),
                               [vehicle])
        lidarMsg.fillBuffer(lidarBuf,
                            scanData,
                            self.lidar,
                            vehicle.getAngle(),
                            100)
        self.lidarStream.send(lidarBuf)

class PosePublisher:
    def __init__(self, obj, stream):
        self.obj = obj
        self.poseStream = stream

    def publish(self):
        poseBuf = self.poseStream.getBuffer(28)
        poseMsg = PoseMsg()
        poseMsg.storePose(self.obj)
        poseMsg.fillBuffer(poseBuf)
        self.poseStream.send(poseBuf)


class VehicleNode:
    def __init__(self, mcast, port, obj, lidar):
        self._running = False
        self._thread = None

        self.poseStream = OutputDataStream(mcast, port);
        self.posePub = PosePublisher(obj, self.poseStream)

        # Static allocation, each obj unique address
        # attributes within the object increment port

        self.lidarStream = OutputDataStream(mcast, port+1)
        self.lidarPub = LidarPublisher(lidar, self.lidarStream)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self.run)
            self._thread.start()
        else:
            print("Already running")

    def run(self):
        while self._running:
            self.posePub.publish()
            self.lidarPub.publish()
            time.sleep(0.3)

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        print("Worker stopped")
