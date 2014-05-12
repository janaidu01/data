import datetime
import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from .alerts_dao import AlertsDao
from .stop_dao import StopDao
from .headsign_dao import StopHeadsignDao

from ott.utils import date_utils

from gtfsdb import StopTime
from gtfsdb import Trip


class StopScheduleDao(BaseDao):
    ''' StopScheduleDao data object is contains all the schedule data at a given stop
    '''
    def __init__(self, stop, stoptimes, headsigns, route_id=None):
        super(StopScheduleDao, self).__init__()
        self.stop = stop
        self.stoptimes = stoptimes
        self.headsigns = headsigns
        self.single_route_id   = None
        self.single_route_name = None
        r = self.find_route(route_id)
        if r and r.name:
            self.single_route_id = route_id
            self.single_route_name = r.name

    def find_route(self, route_id):
        ''' @return: RouteDao from the stop
        '''
        
        ret_val = None
        if self.stop:
            ret_val = self.stop.find_route(route_id)
        return ret_val


    @classmethod
    def get_stop_schedule(cls, session, stop_id, date=None, route_id=None, agency="TODO"):
        '''
        '''
        ret_val = None

        stop = None
        headsigns = {}
        stoptimes = []

        # step 1: figure out date and time
        is_now = False
        if date is None:
            date = datetime.date.today()
            is_now = True
        now = datetime.datetime.now()

        # step 2: get the stop schedule
        stops = StopTime.get_departure_schedule(session, stop_id, date, route_id)

        # step 4: loop through our queried stop times
        for i, st in enumerate(stops):
            if cls.is_boarding_stop(st):
                # 4a: capture a stop object for later...
                if stop is None:
                    stop = StopDao.from_stop_orm(stop=st.stop, agency=agency, detailed=True)

                # 4b: only once, capture the route's different headsigns shown at this stop
                #     (e.g., a given route can have multiple headsignss show at this stop)
                id = StopHeadsignDao.unique_id(st)
                if not headsigns.has_key(id):
                    # make a new headsign
                    h = StopHeadsignDao(st)
                    h.sort_order += i
                    h.id = id
                    headsigns[id] = h

                # 4c: add new stoptime to headsign cache 
                time = cls.make_stop_time(st, id, now, i+1)
                stoptimes.append(time)
                headsigns[id].last_time = st.departure_time
                headsigns[id].num_trips += 1

        # step 5: if we don't have a stop (and thus no stop times), we have to get something for the page to say no schedule today 
        if stop is None:
            stop = StopDao.from_stop_id(session=session, stop_id=stop_id, agency=agency, detailed=True)

        # step 6: build the DAO object (assuming there was a valid stop / schedule based on the query) 
        ret_val = StopScheduleDao(stop, stoptimes, headsigns, route_id)

        return ret_val

    @classmethod
    def get_stop_schedule_from_params(cls, session, stop_params):
        ''' will make a stop schedule based on values set in ott.utils.parse.StopParamParser 
        '''
        #import pdb; pdb.set_trace()
        ret_val = cls.get_stop_schedule(session, stop_params.stop_id, stop_params.date, stop_params.route_id, stop_params.agency)
        return ret_val

    @classmethod
    def make_stop_time(cls, stoptime, headsign_id, now, order):
        ''' {"t":'12:33am', "h":'headsign_id;, "n":[E|N|L ... where E=Earlier Today, N=Now/Next, L=Later]}
        '''
        time = date_utils.military_to_english_time(stoptime.departure_time)
        #stat = date_utils.now_time_code(stoptime.departure_time, now)
        #ret_val = {"t":time, "h":headsign_id, "n":stat, "o":order}
        ret_val = {"t":time, "h":headsign_id, "o":order}
        return ret_val

    @classmethod
    def is_boarding_stop(cls, stop_time):
        ret_val = True
        try:
            if stop_time.pickup_type == 1 or stop_time.departure_time is None:
                ret_val = False
        except:
            pass
        return ret_val



###########################
##### OLD CODE
###########################

class x():

    @classmethod
    def make_alerts(cls, headsign_cache, session):
        ret_val = []

        rte_visited = []
        rte_has_alerts = []
        for h in headsign_cache.values():
            rte = str(h.route_id)
            has_alert = False

            # step 1: only call the alert service once per route (e.g., many headsigns per route)
            if rte not in rte_visited:
                rte_visited.append(rte)

                # step 2: first time seeing this route id, so call the alert service
                alerts = AlertsResponse.get_route_alerts(session, rte)

                # step 3: if this route has alerts, we'll append that list to our ret_val list
                #         and also mark the 'has_alerts' array with this route for future iterations
                if alerts:
                    ret_val = ret_val + alerts
                    rte_has_alerts.append(rte)

            # step 4: mark headsigns for route X as either having alerts or not  
            if rte in rte_has_alerts:
                has_alert = True
            h.has_alert = has_alert

        return ret_val
