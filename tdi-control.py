"""
USAGE:
    python tdi-control [OPTIONS]

OPTIONS:

    -h, --help
        Display this help message.

    --task=FILE
        The file containing config data about the frequency, position, velocity

    --name=NAME
        The (folder-)name of the current run

"""

from common.logger import Logger
from control.clients import *
from control.run import RunConfig, Run

from threading import Thread
import getopt, sys, time, os

logger = Logger.get_logger()

def usage():
    print(__doc__)

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

        cam = CameraClient()

        xps.run_id = r.id

        if not r.freq is None:
            cam.send_command("freq", r.freq)

        xps.change_parameter(r.pos, r.vel)

        t1 = Thread(target=xps.move_and_gather, args=())
        t2 = Thread(target=cam.send_command, args=("start", ))

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
        cam.send_command("stop", subdir + "\\" + r.id)

        time.sleep(2)

    logger.info("cli: finished")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "name=", "task=", "show-config"])

    except getopt.GetoptError as err:
        print("Error: ", err)
        sys.exit(2)

    name = task = None

    for o, a in opts:

        if o in "--name":
            name = a

        elif o in "--task":
            a += ".json"

            if not os.path.isabs(a):
                a = os.path.dirname(os.path.abspath(__file__))+ "\\tasks\\" + a

            if os.path.exists(a):
                task = a
            else:
                print("Task file %s does'nt exist!", a)

        elif o in "--show-config":
            print(vars(Config))

        else:
            usage()
            sys.exit(2)

    if task is None:
        print("No task!")
        usage()
        sys.exit()

    start(task, name)

if __name__ == "__main__":
    main()
