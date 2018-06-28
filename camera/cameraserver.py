import signal
import socket
import sys
import time
from threading import Thread

from camera.neunkdemo import Neunkdemo
from common.config import Config
from common.logger import Logger
from common.package import Command, Response

logger = Logger.get_logger()


def exit_handler(signal, frame):
    logger.info("camera: closed by user")
    sys.exit(0)

class CameraServer:

    def __init__(self):
        logger.debug("camera: started")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((Config.get("CAM_HOST"), Config.get("CAM_PORT")))
        self.socket.listen(10)

        self.program = Neunkdemo()

    def __del__(self):
        logger.debug('camera: closed')

        try:
            self.socket.close()
        except:
            pass

    def start(self):
        signal.signal(signal.SIGINT, exit_handler)

        while True:
            conn, addr = self.socket.accept()
            logger.debug("camera: connected by %s", addr)

            self.thread = Thread(target=self.receive, args=(conn, addr))
            self.thread.start()

            time.sleep(1)
        return

    def receive(self, connection, addr):

        bytes_rcved = 0
        data        = ""
        msg_len     = int(connection.recv(Command.MSG_LENGTH))

        if (msg_len <= 0):
            raise RuntimeError("message error")

        while bytes_rcved < msg_len:
            chunk = connection.recv(min(msg_len - bytes_rcved, 2048))

            if chunk == b'':
                raise RuntimeError("socket connection broken")

            data += chunk.decode('utf-8')
            bytes_rcved += len(chunk)


        if(len(data) <= 0):
            logger.error("server: no data")
            raise RuntimeError("no data")

        logger.debug("camera: received \'%s\'", data)

        package  = Command.from_string(data)

        try:
            if package.command == "freq":
                res = self.program.set_frequency(package.value)

            elif package.command == "start":
                res = self.program.profile_start()

            elif package.command == "save":
                res = self.program.stop_store_sector(package.value)

            elif package.command == "stop":
                res = self.program.profile_stop()

            elif package.command == "test":
                res = self.program.test()

            else:
                logger.warning("camera: no suitable task found for 'task'")
                return

        except Exception:
            res = False
            logger.error('camera: Error during task execution')

        response = Response(package, res)

        logger.debug("camera: send message \'%s\'", response)

        total_sent = 0
        while total_sent < len(str(response).encode('utf-8')):
            sent = connection.send(str(response).encode('utf-8')[total_sent:])
            if sent == 0:
                logger.error("server: socket connection broken")
                raise RuntimeError("connection broken")

            total_sent += sent

        connection.close()
        logger.debug("camera: disconnected")

        return
