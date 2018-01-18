import socket, time, msvcrt
from threading import Thread

from camera.neunkdemo import Neunkdemo
from common.config import Config
from common.logger import Logger
from common.package import Command, Response

logger = Logger.get_logger()

class Server:
    SCRIPT = "G:\\data\\pywinauto\\tdi-Neunkdemo.py"

    def __init__(self):
        logger.info("camera: started")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((Config.get("CAM_HOST"), Config.get("CAM_PORT")))
        self.socket.listen(10)

    def __del__(self):
        logger.info('camera: closed')

        try:
            self.socket.close()
        except:
            pass

    def start(self):
        while True:
            if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode():
                logger.debug('camera: aborted by user')
                break

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

        logger.info("camera: received \'%s\'", data)

        program = Neunkdemo()
        command  = Command.from_string(data)
        response = Response(command, program.run(command))

        logger.info("camera: send message \'%s\'", response)

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
