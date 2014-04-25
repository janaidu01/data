import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from .route_dao import RouteDao
from .alerts_dao import AlertsDao

class StopListDao(BaseDao):
    ''' List of StopDao data objects ... both list and contents ready for marshaling into JSON
    '''
    def __init__(self, stops):
        super(StopListDao, self).__init__()
        self.stops = stop_list
        self.count = len(stop_list)

    @classmethod
    def from_routestops_orm(cls, route_stops):
        ''' make a StopListDao based on a route_stops object
        '''
        ret_val = None
        if route_stops and len(route_stops) > 0:
            from sqlalchemy.orm import object_session
            from gtfsdb import Stop
            session = object_session(route_stops[0])
            stops = []
            for rs in routes_stops:
                sorm = session.query(Stop).filter(Stop.stop_id == rs.stop_id)
                sdao = StopDao.from_stop_orm(stop=sorm, order=rs.order)
                stops.append(sdao)
            ret_val = StopListDao(stops)
        return ret_val


class StopDao(BaseDao):
    ''' Stop data object that is  ready for marshaling into JSON

    "stop_id":"7765",
    "name":"SW 6th & Jefferson",
    TODO "city":"Portland",
    "description": "X bound street in Portland
    "lat":"45.514868",
    "lon":"-122.680762",

    "stop_img_url" : "",
    "planner_url"  : "",
    "tracker_url"  : "",

    "amenities": [
        "Shelter",
        "TransitTracker Sign",
        "Schedule Display",
        "Lighting at Stop",
        "CCTV",
        "Telephone",
        "Front-door Landing Paved",
        "Back-door Landing Paved",
        "Sidewalk",
        "Traffic Signal",
        "Crosswalk",
        "Curbcut"
    ]
    ,
    "routes": [
        {"route_id":1, "name":"1-Vermont", "route_url":"http://trimet.org/schedules/r001.htm", "arrival_url":"http://trimet.org/arrivals/tracker.html?locationID=7765&route=001"}
    '''
    def __init__(self, stop, amenities, routes, alerts=None, distance=0.0, order=0):
        super(StopDao, self).__init__()

        #import pdb; pdb.set_trace()
        self.copy_basics(self.__dict__, stop)
        self.distance = distance
        self.order = order
        self.set_alerts(alerts)

        self.amenities = amenities
        if amenities and len(amenities) > 0:
            self.has_amenities = True
        else:
            self.has_amenities = False

        # process the list of routes serving the stop
        self.routes = []
        rte_cache = []
        '''
        if stop.routes is not None:
            for r in stop.routes:
                rs = RouteDao(r, stop, session)
                self.routes.append(rs)
        '''
        if stop.headsigns is not None:
            for h in stop.headsigns:
                if h[0].route_id not in rte_cache:
                    rte_cache.append(h[0].route_id)
                    rs = RouteDao.from_route_orm(h[0])
                    self.routes.append(rs)

        self.alerts = []


        '''
        if templates:
            self.arrival_url, self.has_arrival_url = templates.get_arrival_url(self)
            self.from_planner_url, self.has_from_planner_url = templates.get_from_planner_url(self)
            self.to_planner_url, self.has_to_planner_url = templates.get_to_planner_url(self)
            self.stop_img_url, self.has_stop_img_url = templates.get_stop_img_url(self)
            self.map_url, self.has_map_url = templates.get_map_url(self)
        '''

    @classmethod
    def copy_basics(cls, tgt, src):
        tgt['stop_id'] = src.stop_id
        tgt['name'] = src.stop_name
        tgt['description'] = src.stop_desc
        tgt['type'] = src.location_type
        tgt['lat'] = src.stop_lat
        tgt['lon'] = src.stop_lon


    @classmethod
    def from_stop_orm(cls, stop, distance=0.0, order=0):
        ''' make a StopDao from a stop object and session ... and maybe templates
        '''

        # step 1: query db for stop amenity names
        #  -TODO- cache this stuff???
        amenities = []
        for f in stop.stop_features:
            amenities.append(f.stop_feature_type.feature_name)
        amenities = sorted(list(set(amenities)))  # sorted and distinct (set) list of attributes 

        from sqlalchemy.orm import object_session
        alerts = []
        #alerts = AlertsDao.get_stop_alerts(object_session(stop), stop.stop_id)

        # step 2: query db for route ids serving this stop...
        routes = None
        ret_val = StopDao(stop, amenities, routes, alerts, distance, order)

        return ret_val


    @classmethod
    def from_stop_id(cls, session, stop_id, distance=0.0, agency="TODO"):
        ''' make a StopDao from a stop_id and session ... and maybe templates
        '''
        #import pdb; pdb.set_trace()
        from gtfsdb import Stop
        stop = session.query(Stop).filter(Stop.stop_id == stop_id).one()
        ret_val = cls.from_stop_orm(stop, distance)
        return ret_val

