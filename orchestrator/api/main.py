import cherrypy
import logging
import socket
import configparser
from auth import AuthController, require
from cherrypy import tools
from plugins import import_plugin
from geopy.geocoders import Nominatim
from geojson import Feature, Point, FeatureCollection
from geopy.exc import GeocoderTimedOut
from plugins.save.mongo_driver import DBDriver
import hashlib


class API(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }

    auth = AuthController()

    def __init__(self):
        self.geolocator = Nominatim()
        self.db_driver = DBDriver()
        self.logger = logging.getLogger("spider.server")
        self.plugins = import_plugin()
        self.config = configparser.ConfigParser()
        self.config.read('../main.py')

    def __get_geocode(self, address):
        _location = None
        _feature = None
        try:
            try:
                _location = self.geolocator.geocode("{}, France".format(address))
            except Exception as e:
                self.logger.error(str(e))
            else:
                self.logger.debug(_location)
            # self.logger.info("address={}".format(_ad['address']))
            # self.logger.info("_location={}".format(_location))
            _feature = Feature(geometry=Point((_location.longitude, _location.latitude)))
        except socket.timeout:
            self.logger.warning("Timeout during retrieving geocode for {}".format(address))
        except GeocoderTimedOut:
            self.logger.warning("Timeout during retrieving geocode for {}".format(address))
        return _feature

    @cherrypy.expose
    @tools.json_out()
    def index(self):
        return {"version": self.config['global']['version'], "tree": ["/", "/data"]}

    @cherrypy.expose
    @tools.json_out()
    @require()
    def data(self, geoid=None):
        # cherrypy.response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:4000"
        if id:
            return self.db_driver.get(geo_id=geoid)
        return self.db_driver.get()

    @cherrypy.expose
    @tools.json_out()
    @require()
    def features(self, choice=None):
        features = list()
        for _ad in self.db_driver.get():
            _feature = _ad['feature']
            coord = str(_feature['geometry']['coordinates']).encode('utf-8')
            h_coord = hashlib.sha224(coord).hexdigest()
            self.logger.debug("h_coord: {}".format(h_coord))
            # _feature['id'] = _ad['id']
            _feature['id'] = h_coord
            self.logger.info(_feature)
            features.append(_feature)
        return FeatureCollection(features)

    @cherrypy.expose
    @tools.json_out()
    @require()
    def sync(self):
        # cherrypy.response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:4000"
        ads = []
        for _plug_name, _plugin in self.plugins.items():
            try:
                _ads = _plugin.__driver__.compute()
                for _ad in _ads:
                    _ad['feature'] = self.__get_geocode(_ad['address'])
                    if self.db_driver.insert(_ad):
                        ads.append(_ad)
            except AttributeError as e:
                self.logger.error('Unable to open plugin {}'.format(_plug_name))
                self.logger.debug(str(e))

        return {"action": "sync", "number": len(ads)}
        # return FeatureCollection(ads)

    @cherrypy.expose
    @tools.json_out()
    @require()
    def purge(self):
        delete_count = self.db_driver.purge()
        return {"action": "purge", "number": delete_count}
