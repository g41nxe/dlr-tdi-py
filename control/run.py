from datetime import datetime
import json, os
from config import Config

class Run:

    id   = None
    freq = None
    pos  = []
    vel  = None

    def __init__(self, freq, pos, vel, id):
        self.freq = freq
        self.pos = pos
        self.vel = vel
        self.id = id

    def unpack(self):
        return (self.freq, self.pos, self.vel, self.id)

class RunConfig:

    id         = None
    iterations = []
    timestamp  = None

    def __init__(self, file):

        self.timestamp = datetime.now()
        self.load(file)

    def load(self, file):

        if not os.path.isabs(file) or not os.path.exists(file):
            raise ValueError

        data = json.load(open(file, 'r'))

        self.id = data['id']

        for runs in data['runs']:

            for (k, v) in runs['config']:
                Config.set(k, v)

            for run in runs['run']:

                if 'frequency' not in run:
                    run['frequency'] = None

                if 'velocity' not in run:
                    run['velocity'] = None

                if 'position' not in run:
                    run['position'] = []

                position = []
                name = self.timestamp.strftime('%H%M%S') + '_' + self.id + '_' + str(len(self.iterations))

                for (grp, pos) in run['position']:
                    position.append((Config.get(grp), pos))

                r = Run(run['frequency'], position, run['velocity'], name)

                self.iterations.append(r)

    def getRuns(self):
        return self.iterations






