"""
USAGE:
    python tdi-control [OPTIONS]

OPTIONS:
    -h, --help
        Display this help message.
    --start
        Start measurement run
    --show-config
"""

from control.clients import *
import getopt, sys
from threading import Thread

logger = Config.get_logger()

def usage():
    print(__doc__)

def start(subdirectoy=None):
    xps = XPSClient()

    id = datetime.now().strftime("%H%M%S")
    logger.info("cli: id %s\\%s", subdirectoy, id)

    for f in Config.FREQUENCIES:
        logger.info("cli: frequency: %s Hz", f)
        i = 0
        for row in Config.POSITIONS:
            logger.info("cli: positions %s", row)

            cam = CameraClient()
            xps.run_id = id + "_" + str(f) + "hz_position" + str(i)

            cam.send_command("freq", f)
            xps.change_position(row)

            t1 = Thread(target=xps.move, args=())
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

            xps.save_gathering_data(subdirectoy)
            cam.send_command("stop", subdirectoy + "\\" + xps.run_id)

            i += 1

    path = Config.XPS_RESULT_PATH + "\\" + datetime.now().strftime("%d%m%y")

    if not subdirectoy is None:
        path += "\\" + subdirectoy

    Config.save_to_file(path, id)
    logger.info("cli: finished")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "start=", "show-config"])

    except getopt.GetoptError as err:
        print("Error: %s", err)
        usage()
        sys.exit(2)

    for o, a in opts:

        if o in "--start":
            start(a)

        elif o in "--show-config":
            print(vars(Config))

        else:
            usage()
            sys.exit(2)


if __name__ == "__main__":
    main()
