import socket, ftplib, os
from datetime import datetime

from common.config  import Config
from common.logger import Logger
from common.package import Response, Command
from control.xps    import XPS

logger = Logger.get_logger()

class XPSClient:

    def __init__(self):
        self.xps = XPS()
        self.socket_id = -1

        try:
            logger.debug("client: connect to xps %s:%s", Config.get("XPS_HOST"), Config.get("XPS_PORT"))
            self.socket_id = self.xps.TCP_ConnectToServer(Config.get("XPS_HOST"), Config.get("XPS_PORT"), 10)
            logger.debug("client: xps socket id: %s", self.socket_id)

        except Exception as e:
            logger.error("client: cannot connect to xps %s")
            raise RuntimeError(e)

        self.__homing()

    def __del__(self):
        logger.debug("client: disconnect from XPS")

        self.xps.TCP_CloseSocket(self.socket_id)

    def __homing(self):
        try:
            # homing
            logger.debug('client: xps homing')

            for group in [Config.get("CAM_X_GROUP"), Config.get("CAM_Y_GROUP"), Config.get("CAM_Z_GROUP"), Config.get("FP_GROUP")]:
                logger.debug('client: init xps %s', group)
                self.xps.GroupInitialize(self.socket_id, group)
                logger.debug('client: home-search %s', group)
                self.xps.GroupHomeSearch(self.socket_id, group)

        except Exception as e:
            logger.error("client: init error")
            raise RuntimeError(e)

    def change_parameter(self, pos=[], vel=None):

        try:
            # acceleration + velocity
            if not vel is None:
                logger.debug("client: change velocity to %s", vel)
                self.xps.PositionerSGammaParametersSet(self.socket_id,
                                                       Config.get("FP_GROUP") + '.' + Config.get("FP_GROUP_NAME"),
                                                       vel, Config.get("FP_ACCELERATION"), Config.get("FP_JERKTIME")[0],
                                                       Config.get("FP_JERKTIME")[1])

            # position for every axis
            if len(pos) > 0:
                logger.debug("client: change positions to %s", pos)
                for group, position in pos:
                    self.xps.GroupMoveAbsolute(self.socket_id, group, position)

        except Exception as e:
            logger.error("client: XPS change position error")
            raise RuntimeError(e)

        return True

    def init_event(self):
        logger.debug('client: init xps events')

        types = []
        for type in Config.get("XPS_DATA_TYPES"):
            types.append(Config.get("FP_GROUP") + "." + Config.get("FP_GROUP_NAME") + "." + type)

        self.xps.GatheringConfigurationSet(self.socket_id, types)
        logger.debug("client: set xps config %s", types)

        self.xps.EventExtendedConfigurationTriggerSet(self.socket_id, [Config.get("XPS_TRIGGER")], ['2'], ['0'], ['0'], ['0'])
        logger.debug("client: set xps event trigger")

        self.xps.EventExtendedConfigurationActionSet(self.socket_id, ["GatheringRun"], ['50000'], ['1'], ['0'], ['0'])
        logger.debug("client: set xps event action")

    def move_and_gather(self):
        logger.debug("client: move fp %s times from %s to %s", Config.get("ITERATIONS"), Config.get("FP_START"), Config.get("FP_END"))

        self.init_event()

        try:
            self.xps.GatheringReset(self.socket_id)
            logger.debug("client: reset xps data")

            self.xps.EventExtendedStart(self.socket_id)

            for i in range(Config.get("ITERATIONS")):
                self.xps.GroupMoveAbsolute(self.socket_id, Config.get("FP_GROUP"), [Config.get("FP_START")])
                self.xps.GroupMoveAbsolute(self.socket_id, Config.get("FP_GROUP"), [Config.get("FP_END")])

            self.xps.GatheringStopAndSave(self.socket_id)
            logger.debug("client: save xps data")


        except Exception as e:
            logger.error("client: XPS move error")
            logger.debug(e)
            raise RuntimeError(e)

        return True

    def save_gathering_data(self, subdirectory=None, name=None):
        try:
            directory = Config.get("XPS_RESULT_PATH") + "\\" + datetime.now().strftime("%d%m%y")

            if not subdirectory is None:
                directory += "\\" + subdirectory

            filename = name + ".gather"

            file = directory + "\\" + filename

            if not os.path.exists(directory):
                os.makedirs(directory)

            handle = open(file, 'wb').write

            ftp = ftplib.FTP(Config.get("XPS_HOST"))
            ftp.login(Config.get("XPS_USER"), Config.get("XPS_PASSWORD"))
            ftp.cwd(Config.get("XPS_FTP_PATH"))
            ftp.retrbinary("RETR " + Config.get("XPS_FTP_FILE"), handle)
            ftp.quit()

        except Exception as e:
            logger.error('client: cannot save gathering file %s')
            raise RuntimeError(e)

        logger.debug("client: gathering data saved to %s", file)

class CameraClient:

    def __connect(self):
        logger.debug("client: connect to camera")

        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((Config.get("CAM_HOST"), Config.get("CAM_PORT")))

        except Exception as e:
            logger.error("client: cannot connect to camera")
            raise RuntimeError(e)

        return connection

    def __disconnect(self, connection):
        logger.debug("client: disconnect from camera")
        try:
            connection.close()
        except:
            pass

    def __read_response(self, connection):
        logger.debug("client: ready to receive")

        try:
            msg_len = int(connection.recv(Response.MSG_LENGTH))
        except Exception as e:
            logger.error("client: response error %s")
            raise RuntimeError(e)

        if (msg_len <= 0):
            raise RuntimeError("message error")

        bytes_rcved = 0
        data        = ""

        if (msg_len <= 0):
            raise RuntimeError("message error")

        while bytes_rcved < msg_len:
            chunk = connection.recv(min(msg_len - bytes_rcved, 2048))
            if chunk == b'':
                logger.error("client: socket connection broken")
                raise RuntimeError("connection broken")

            data += chunk.decode('utf-8')
            bytes_rcved += len(chunk)

        if (len(data) > 0):
            logger.debug("client: received \'%s\'", data)
        else:
            logger.error("client: no response received")
            raise RuntimeError("no response")

        return

    def set_frequency(self, freq):
        self.__send_command("freq", freq)

    def profile_start(self):
        self.__send_command("start")

    def profile_stop(self, filename):
        self.__send_command("start", filename)

    def __send_command(self, command, value=""):

        connection = self.__connect()

        package = Command(command, value)
        logger.debug("client: send message \'%s\'", str(package))

        try:
            connection.send(str(package).encode("utf-8"))

        except Exception as e:
            logger.error("client: cannot send to camera")
            raise RuntimeError(e)

        self.__read_response(connection)
        self.__disconnect(connection)

        return

