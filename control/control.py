from common.logger import Logger
from control.clients import *
from control.run import RunConfig, Run

from threading import Thread
import time

logger = Logger.get_logger()

class Control:

    @staticmethod
    def start(run_file, subdir=None):
        xps = XPSClient()

        cfg = RunConfig(run_file)

        if subdir is None:
            subdir = "default"

        logger.info("cli: run %s\\%s with config %s", subdir, cfg.id, run_file)

        for r in cfg.getRuns():

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
            cam.profile_stop(subdir + "\\" + r.id)

            time.sleep(2)

        logger.info("cli: finished")