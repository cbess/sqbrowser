import cPickle as pickle
import os


class Config:
    def __init__(self, path=None):
        self.path = path
        self.db_path = None
        self.src_path = None

    def save(self):
        pickle.dump(self, open(self.path, 'w'))

    def load(self):
        if not os.path.isfile(self.path):
            return
        cfg = pickle.load(open(self.path, 'r'))
        self.db_path = getattr(cfg, 'db_path')
        self.src_path = getattr(cfg, 'src_path')