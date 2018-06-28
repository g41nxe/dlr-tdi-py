import os
from datetime import datetime

from common.config import Config
from common.logger import Logger
from pywinauto.application import Application
from pywinauto.timings import TimeoutError, Timings

logger = Logger.get_logger()

class Neunkdemo:

    def __init__(self):

        Timings.Slow()

        self.base_path  = Config.get("CAM_RESULT_PATH")
       
        self.app        = Application(backend="win32").connect(path=Config.get("CAM_PROGRAM_PATH"))
        self.dlg        = self.app.Test9k

        self.frequency = self.dlg.Spinner4.get_buddy_control().text_block()

        return

    def set_frequency(self, value):

        stop = self.dlg.ProfileStop

        if stop.is_enabled() and stop.is_visible():
            stop.click()

        self.dlg.Spinner4.get_buddy_control().set_text(value)
        self.dlg.Spinner4.get_buddy_control().type_keys("{ENTER}")

        self.frequency = self.dlg.Spinner4.get_buddy_control().text_block()
        logger.info("9kdemo: frequency set to %s", self.frequency)

        return True

    def profile_start(self):

        start = self.dlg.ProfileStart
        stop  = self.dlg.ProfileStop
        qss   = self.dlg.QSS

        if stop.is_enabled() and stop.is_visible():
            stop.click()
            logger.debug("9kdemo: stop button clicked")

        if not qss.is_visible():
            logger.error("9kdemo: qss not visible")
            return False

        qss.check_by_click()
        logger.debug("9kdemo: qss button clicked")

        if start.is_enabled() and start.is_visible():
            start.Wait('visible enabled', timeout=5)
            start.click()
            logger.debug("9kdemo: start button clicked")
        else:
            logger.error("9kdemo: start button not enabled")
            return False

        logger.info("9kdemo: profiling started")

        return True

    def stop_store_sector(self, filename=None):

        store     = self.dlg.StopStoreSector
        filename  = filename + ".spot"
        directory = self.base_path + "\\" + datetime.now().strftime("%d%m%y")

        if not os.path.exists(directory):
            os.makedirs(directory)

        if store.is_visible() and store.is_enabled():
            store.click()
            logger.debug("9kdemo: click store button")
        else:
            logger.error("9kdemo: store not visible")
            return False

        self.app.SpotFile.Wait('ready', timeout=5)

        path = self.app.SpotFile.Edit
        save = self.app.SpotFile.Speichern

        logger.debug("9kdemo: set path")

        path.set_text(directory + "\\" + filename)
        save.click()

        try:
           self.app.SpotFile.WaitNot('visible', timeout=5)
        except TimeoutError:
            logger.warning("9kdemo: file already existed")

            ja = self.app.SpotFile.Ja
            ja.Wait('enabled visible', timeout=5)
            ja.click()
            logger.debug("9kdemo: ja button clicked")

        try:
            self.dlg.Wait('ready', timeout=5)
        except TimeoutError:
            logger.error("9kdemo: main window now tready")
            return False

        logger.info("9kdemo: data saved to %s\%s", directory, filename)

        return True

    def profile_stop(self):

        stop      = self.dlg.ProfileStop

        if stop.is_enabled() and stop.is_visible():
            stop.click()
            logger.debug("9kdemo: stop button clicked")
        else:
            logger.warning("9kdemo: stop button not enabled")

        logger.info("9kdemo: profiling stopped")

        return True

    def test(self):
        try:
            if self.app.Test9k.is_visible():
                return True

        except Exception:
            pass

        return False
