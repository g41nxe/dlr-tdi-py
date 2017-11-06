import socket, sys, logging, ftplib, os
from datetime import datetime

from common.config  import Config
from common.package import Response, Command
from control.xps    import XPS

logger = logging.getLogger(__name__)
logger.setLevel(Config.LOG_LEVEL)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(Config.LOG_LEVEL)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)

class XPSClient:

    frequency = None

    def __init__(self):
        self.xps = XPS()
        self.socket_id = -1

        try:
            logger.debug("client: connect to xps %s:%s", Config.XPS_HOST, Config.XPS_PORT)
            self.socket_id = self.xps.TCP_ConnectToServer(Config.XPS_HOST, Config.XPS_PORT, 10)
            logger.debug("client: xps socket id: %s", self.socket_id)

        except Exception as e:
            logger.error("client: cannot connect to xps %s")
            raise RuntimeError(e)

        self.__init()

    def __del__(self):
        logger.debug("client: disconnect from XPS")

        self.xps.TCP_CloseSocket(self.socket_id)

    def __init(self):
        try:
            # @todo set fp speed + acc

            # homing
            logger.debug('client: xps homing')

            for group in [Config.CAM_X_GROUP, Config.CAM_Y_GROUP, Config.CAM_Z_GROUP, Config.FP_GROUP]:
                logger.debug('client: init xps %s', group)
                self.xps.GroupInitialize(self.socket_id, group)
                logger.debug('client: home-search %s', group)
                self.xps.GroupHomeSearch(self.socket_id, group)

            # setup event for data recording

            self.xps.PositionerSGammaParametersSet(self.socket_id, Config.FP_GROUP + '.' + Config.FP_GROUP_NAME,
                                                   Config.FP_VELOCITY, Config.FP_ACCELERATION, Config.FP_JERKTIME[0], Config.FP_JERKTIME[1])

            self.init_event()

        except Exception as e:
            logger.error("client: init error")
            raise RuntimeError(e)

    def move_to_position_and_move(self, row):
        logger.info("client: move xps to %s", row)

        try:
            for group, position in row:
                self.xps.GroupMoveAbsolute(self.socket_id, group, position)
                logger.debug("client: change %s's position to %s", group, position)

            self.move()

        except Exception as e:
            logger.error("client: XPS move to pos error")
            raise RuntimeError(e)

        return True

    def move(self):

        logger.info("client: move fp %s times from %s to %s", Config.ITERATIONS, Config.FP_START, Config.FP_END)

        try:
            self.xps.GatheringReset(self.socket_id)
            logger.debug("client: reset xps data")

            for i in range(Config.ITERATIONS):
                self.xps.GroupMoveAbsolute(self.socket_id, Config.FP_GROUP, [Config.FP_START])
                self.xps.GroupMoveAbsolute(self.socket_id, Config.FP_GROUP, [Config.FP_END])

            self.xps.GatheringStopAndSave(self.socket_id)

        except Exception as e:
            logger.error("client: XPS jog error")
            raise RuntimeError(e)

        return True


    def init_event(self):
        logger.debug('client: init xps events')

        types = []
        for type in Config.XPS_DATA_TYPES:
            types.append(Config.FP_GROUP + "." + Config.FP_GROUP_NAME + "." + type)

        self.xps.GatheringConfigurationSet(self.socket_id, types)
        logger.debug("client: set xps config %s", types)

        self.xps.EventExtendedConfigurationTriggerSet(self.socket_id, [Config.XPS_TRIGGER], ['2'], ['0'], ['0'], ['0'])
        logger.debug("client: set xps event trigger")

        self.xps.EventExtendedConfigurationActionSet(self.socket_id, ["GatheringRun"], ['50000'], ['1'], ['0'], ['0'])
        logger.debug("client: set xps event action")

        self.xps.EventExtendedStart(self.socket_id)
        logger.debug("client: set xps event start")

    def save_gathering_data(self):
        try:
            directory = Config.XPS_RESULT_PATH + "\\" + datetime.now().strftime("%d%m%y")

            timestamp = datetime.now().strftime('%H%M%S')
            filename  = timestamp + "_" + self.frequency + "hz" + ".view"
            file      = directory + "\\" + filename

            if not os.path.exists(directory):
                os.makedirs(directory)

            handle = open(file, 'wb').write

            ftp = ftplib.FTP(Config.XPS_HOST)
            ftp.login(Config.XPS_USER, Config.XPS_PASSWORD)
            ftp.cwd(Config.XPS_FTP_PATH)
            ftp.retrbinary("RETR " + Config.XPS_FTP_FILE, handle)
            ftp.quit()

        except Exception as e:
            logger.error('client: cannot save gathering file %s')
            raise RuntimeError(e)

        logger.info("client: gathering data saved to %s", file)

        return timestamp

class CameraClient:

    def __connect(self):
        logger.debug("client: connect to camera")

        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((Config.CAM_HOST, Config.CAM_PORT))

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
            logger.debug("client: received '%s'", data)
        else:
            logger.error("client: no response received")
            raise RuntimeError("no response")

        return

    def send_command(self, command, value=""):

        connection = self.__connect()

        package = Command(command, value)
        logger.debug("client: send message  '%s'", str(package))

        try:
            connection.send(str(package).encode("utf-8"))

        except Exception as e:
            logger.error("client: cannot send to camera")
            raise RuntimeError(e)

        self.__read_response(connection)
        self.__disconnect(connection)

        return

