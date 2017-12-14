"""
USAGE:
    python tdi-control [OPTIONS]

OPTIONS:

    -h, --help
        Display this help message.

    --start=NAME
        Start measurement run

    --show-config
        Print config file

    --frequency=FREQ
        single = 9615
        small  = 10  values between [2786, 9615]
        full   = 255 values between [2786, 9615]

    --position=POS
        single  = ( 259.849, 7.1, 101.615 )
        focus   = ( 259.849, 5 .. 5.5 .. 6 .. 9, 101.615 )


"""

from common import config
from control.clients import *
import getopt, sys
from threading import Thread
import time

logger = Config.get_logger()

def usage():
    print(__doc__)

def start(subdirectoy=None, freq=None, pos=None):
    xps = XPSClient()

    id = datetime.now().strftime("%H%M%S")
    logger.info("cli: id %s\\%s", subdirectoy, id)

    if freq is None:
        freq = Config.DEFAULT_FREQUENCY
    if pos is None:
        pos = Config.DEFAULT_POSITION

    for f in Config.FREQUENCIES[freq]:
        logger.info("cli: frequency: %s Hz", f)
        i = 0
        for row in Config.POSITIONS[pos]:
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

            time.sleep(2)
            i += 1

    path = Config.XPS_RESULT_PATH + "\\" + datetime.now().strftime("%d%m%y")

    if not subdirectoy is None:
        path += "\\" + subdirectoy

    config.save_to_file(path, id)
    logger.info("cli: finished")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "start=", "show-config", "position=", "frequency="])

    except getopt.GetoptError as err:
        print("Error: ", err)
        sys.exit(2)

    name = freq = pos = None

    for o, a in opts:

        if o in "--frequency":
            if not a in Config.FREQUENCIES.keys():
                print("Error: ", a, " is not a valid option for parameter ", 0)
                sys.exit(2)
            else:
                freq = Config.FREQUENCIES[a]

        elif o in "--position":
            if not a in Config.POSITIONS.keys():
                print("Error: ", a, " is not a valid option for parameter ", o)
                sys.exit(2)
            else:
                pos = Config.POSITIONS[a]

        elif o in "--start":
            name = a

        elif o in "--show-config":
            print(vars(Config))

        else:
            print(o)
            usage()
            sys.exit(2)

    for o,a in opts:
        if o in "--start":
            start(name, freq, pos)

if __name__ == "__main__":
    main()
