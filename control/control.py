from common.logger import Logger
from common.config import Config
from clients import *
from run import RunConfig, Run

from threading import Thread
import time, os
from datetime import datetime

logger = Logger.get_logger()

class Control:

    @staticmethod
    def start(run_file, subdir=None):
        xps = XPSClient()

        cfg = RunConfig(run_file)

        if subdir is None:
            subdir = "default"

        logger.info("cli: run %s\\%s with config %s", subdir, cfg.id, run_file)

        runs = cfg.getRuns()

        for idx,r in enumerate(runs):
            logger.info("cli: %s/%s", idx, len(runs))
            logger.info("cli: frequency: %s Hz", r.freq)
            logger.info("cli: positions: %s", r.pos)
            logger.info("cli: velocity: %s", r.vel)
            logger.info("cli: config: %s", r.cfg)

            for (key, value) in r.cfg:
                Config.set(key, value)

            cam = CameraClient()

            xps.run_id = r.id

            if not r.freq is None:
                cam.set_frequency(r.freq)

            xps.change_parameter(r.pos, r.vel)

            repeat = 0
            while True and repeat < 5:
                t1 = Thread(target=xps.move_and_gather, args=())
                t2 = Thread(target=cam.profile_start, args=())

                try:
                    t1.start()
                    t2.start()
                except Exception as e:
                    logger.error(e)
                    raise RuntimeError(e)

                try:
                    t1.join(120)
                    t2.join(120)
                except Exception as e:
                    logger.error(e)
                    raise RuntimeError(e)

                xps.save_gathering_data(subdir, r.id)
                cam.stop_store_sector(subdir + "\\" + r.id)
                cam.profile_stop()

                success = check_files(subdir, r.id)

                if success:
                    break

                repeat = repeat +1
                logger.info("cli: repeat current run")

            time.sleep(2)

        logger.info("cli: finished")

def check_files(subdir, id):
    success = True

    directory = Config.get("XPS_RESULT_PATH") + "\\" + datetime.now().strftime("%d%m%y")

    if not subdir is None:
        directory += "\\" + subdir

    spot   = directory + "\\" + id + ".spot"
    gather = directory + "\\" + id + ".gather"

    if os.path.exists(spot):
        fsize = os.stat(spot).st_size

        logger.debug("cli: spot file: %s KB", fsize / 1024)

        if fsize > 10000000: # 10 MB
            success = True
        else:
            success = False
            logger.error('cli: spot file too small')

    else:
        logger.error("cli: spot file '%s' doesnt exist", spot)
        success = False

    if os.path.exists(gather):
        fsize = os.stat(gather).st_size

        logger.debug("cli: gather file: %s KB", fsize / 1024)

        if fsize > 1000000:  # 1 MB
            success =  success and True
        else:
            success = False
            logger.error('cli: gather file too small')
    else:
        logger.error("cli: gather file '%s' doesnt exist", gather)
        success = False

    if not success:
        os.remove(spot)
        os.remove(gather)

    return success

