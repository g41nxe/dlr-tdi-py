import logging, os, sys
from datetime import date
from pywinauto.application import Application
from pywinauto.timings import TimeoutError

from common.config import Config

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(Config.LOG_LEVEL)
ch.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(Config.LOG_LEVEL)
logger.addHandler(ch)

class Neunkdemo:

    def __init__(self):

        self.base_path  = Config.CAM_RESULT_PATH
       
        self.app        = Application(backend="win32").connect(path=Config.CAM_PROGRAM_PATH)
        self.dlg        = self.app["Test9k"]

        self.frequency = self.dlg.Spinner4.get_buddy_control().text_block()

        return

    def __set_frequency(self, value):

        stop = self.dlg["Profile S&top"]

        if stop.is_enabled():
            stop.click()

        self.dlg.Spinner4.get_buddy_control().set_text(value).type_keys("{ENTER}")

        self.frequency = self.dlg.Spinner4.get_buddy_control().text_block()
        logger.debug("9kdemo: frequency set to %s", self.frequency)

        return True

    def __profile_start(self):

        start = self.dlg["Profile S&tart"]
        stop  = self.dlg["Profile S&top"]
        qss   = self.dlg["QSS"]

        if stop.is_enabled():
            stop.click()

        try:
            qss.wait("visible", timeout=1)
        except TimeoutError:
            return False

        qss.check_by_click()

        if start.is_enabled():
            start.click()
        else:
            return False

        logger.debug("9kdemo: profiling started")

        return True


    def __profile_stop(self, prefix=None):

        stop      = self.dlg["Profile S&top"]
        store     = self.dlg["Stop Store Sector"]
        save      = self.app["Spot-File"]

        filename = prefix + "_" + self.frequency + "hz" + ".spot"
        directory = self.base_path + "\\" + datetime.now().strftime("%d%m%y")

        if not store.is_enabled() or not store.is_visible():
            logger.error("9kdemo: store button not available")
            return False

        if not os.path.exists(directory):
            os.makedirs(directory)

        store.click()

        save.Edit.set_text(directory + "\\" + filename)
        save.Speichern.click()

        if save.is_visible():
            save = self.app["Spot-File"]
            save.Ja.click()

            logger.warning("9kdemo: file already existed")

        if (stop.is_enabled):
            stop.click()

        logger.debug("9kdemo: profiling stopped and saved to %s/%s", directory, filename)

        return True

    def run(self, package):
        task      = package.command
        parameter = package.value

        logger.info("9kdemo: run task '%s' with parameter '%s'", task, parameter)

        try:
            if task == "freq":
                return self.__set_frequency(parameter)

            if task == "start":
                return self.__profile_start()

            if task == "stop":
                return self.__profile_stop(parameter)

        except Exception as e:
            logger.error('9kdemo: Error')
            logger.debug(e)

            return False

        logger.warning("9kdemo: no suitable task found for 'task'")

        return False