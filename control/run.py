from datetime import datetime
import json, os
from common.config import Config

class Run:

    def __init__(self, freq, pos, vel, id, number, cfg):
        self.freq = freq
        self.pos = pos
        self.vel = vel
        self.id = id
        self.number = number
        self.cfg = cfg

    def unpack(self):
        return (self.freq, self.pos, self.vel, self.id, self.number, self.cfg)

class RunConfig:

    def __init__(self, file):
        self.iterations = []
        self.id = None
        self.timestamp = datetime.now()
        self.load(file)

    def load(self, file):

        if not os.path.isabs(file) or not os.path.exists(file):
            raise ValueError

        data = json.load(open(file, 'r'))

        self.id = data['id']

        for run in data['runs']:

            if 'config' not in run.keys():
                run['config'] = []

            param = run['param']

            if 'frequency' not in param.keys():
                param['frequency'] = None

            if 'velocity' not in param.keys():
                param['velocity'] = None

            if 'position' not in param.keys():
                param['position'] = []


            number   =  str(len(self.iterations))
            name     = self.timestamp.strftime('%H%M%S') + '_' + self.id + '_' + number
            position = []

            for (grp, pos) in param['position']:
                position.append((Config.get(grp), pos))

            r = Run(param['frequency'], position, param['velocity'], name, number, run['config'])

            self.iterations.append(r)

    def getRuns(self):
        return self.iterations






