import pickle

import time
import os
import stat


def file_age_in_seconds(pathname):
    return time.time() - os.stat(pathname)[stat.ST_MTIME]


def cache(func):
    fname = ''.join([func.__name__, ".cache"])

    def cachecheck():
        if not os.path.exists(fname) or file_age_in_seconds(fname) > 60:
            cache = func()
            pickle.dump(cache, open('/tmp/awsssh_' + fname, "wb"))
        else:
            cache = pickle.load(open('/tmp/awsssh_' +fname, "rb"))
        return cache

    return cachecheck
