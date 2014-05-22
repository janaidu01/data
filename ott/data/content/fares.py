from datetime import datetime
from datetime import timedelta
import logging
log = logging.getLogger(__file__)

from ott.utils import json_utils

class Fares(object):

    def __init__(self, fare_url, fare_timeout_mins=5040):
        '''
        '''
        log.info("create an instance of {0}".format(self.__class__.__name__))
        self.fare_url = fare_url
        if fare_timeout_mins:
            self.fare_timeout = fare_timeout_mins
        else:
            self.fare_timeout = 5040

        self.last_update = datetime.now() - timedelta(minutes = (self.fare_timeout+10))
        self.content = []
        self.update()

    def update(self):
        try:
            #import pdb; pdb.set_trace()
            if datetime.now() - self.last_update > timedelta(minutes = self.fare_timeout):
                log.debug("updating the fare content")
                self.last_update = datetime.now()
                c = json_utils.stream_json(self.fare_url, extra_path='fares.json')
                if c:
                    self.content = c 
        except Exception, e:
            log.warn("couldn't update the fare content: {}".format(e))
 
    def query(self, fare_type="adult_oneway", def_val=None):
        ''' 
        '''
        ret_val = def_val
        try:
            self.update()
            for c in self.content:
                if fare_type in c:
                    ret_val = c[fare_type]
                    break
        except:
            log.warn("no fare content for fare_type={0}, using default fare of {1}".format(fare_type, def_val))
        return ret_val

