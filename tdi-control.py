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


def usage():
    print(__doc__)

def start(subdirectoy=None):
    xps = XPSClient()

    id = datetime.now().strftime("%H%M%S")

    i = 0
    for f in Config.FREQUENCIES:
        for row in Config.POSITIONS:

            cam = CameraClient()
            logger.info("cli: measurement run for %s Hz", f)

            xps.run_id = id + "_" + str(f) + "hz_position" + str(i)

            cam.send_command("freq", f)
            cam.send_command("start")
            xps.move_to_position_and_move((row))
            xps.save_gathering_data(subdirectoy)
            cam.send_command("stop", subdirectoy + "\\" + xps.run_id)

            i += 1

    path = Config.XPS_RESULT_PATH + "\\" + datetime.now().strftime("%d%m%y")

    if not subdirectoy is None:
        path += "\\" + subdirectoy

    Config.save_to_file(path, id)

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
