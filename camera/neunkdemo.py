import os
from datetime import datetime
from pywinauto.application import Application
from pywinauto.timings import TimeoutError

from common.config import Config
from common.logger import Logger

logger = Logger.get_logger()

class Neunkdemo:

    def __init__(self):

        self.base_path  = Config.get("CAM_RESULT_PATH")
       
        self.app        = Application(backend="win32").connect(path=Config.get("CAM_PROGRAM_PATH"))
        self.dlg        = self.app["Test9k"]

        self.frequency = self.dlg.Spinner4.get_buddy_control().text_block()

        return

    def set_frequency(self, value):

        stop = self.dlg["Profile S&top"]

        if stop.is_enabled():
            stop.click()

        self.dlg.Spinner4.get_buddy_control().set_text(value)
        self.dlg.Spinner4.get_buddy_control().type_keys("{ENTER}")

        self.frequency = self.dlg.Spinne#r4.get_buddy_control().text_block()
        logger.debug("9kdemo: frequency set to %s", self.frequency)

        return True

    def profile_start(self):

        start = self.dlg["Profile S&tart"]
        stop  = self.dlg["Profile S&top"]
        qss   = self.dlg["QSS"]

        if stop.is_enabled():
            stop.click()

        if not qss.is_visible():
            logger.error("9kdemo: qss not visible")
            return False


        qss.check_by_click()

        if start.is_enabled():
            start.click()
        else:
            logger.error("9kdemo: start button not enabled")
            return False

        logger.debug("9kdemo: profiling started")

        return True


    def profile_stop(self, filename=None):

        stop      = self.dlg["Profile S&top"]
        store     = self.dlg["Stop Store Sector"]

        filename = filename + ".spot"
        directory = self.base_path + "\\" + datetime.now().strftime("%d%m%y")

        if not os.path.exists(directory):
            os.makedirs(directory)

        if not store.is_visible() or not store.is_enabled():
            logger.error("9kdemo: store button not available")
            return False

        store.click()

        try:
            self.app["Spot-File"].Wait('visible', timeout=5)
            self.app["Spot-File"].Edit.set_text(directory + "\\" + filename)
            self.app["Spot-File"].Speichern.click()
        except TimeoutError:
            logger.error("9kdemo: save dialog not visible")
            return False

        try:
           self.app["Spot-File"].WaitNot('visible', timeout=5)
        except TimeoutError:
            self.app["Spot-File"].Ja.click()
            logger.warning("9kdemo: file already existed")

        if stop.is_enabled():
            stop.click()
        else:
            logger.debug("9kdemo: stop not enabled")

        logger.debug("9kdemo: profiling stopped and saved to %s\%s", directory, filename)

        return True