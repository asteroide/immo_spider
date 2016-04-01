import cherrypy
import logging
import json
import os
import socket
import configparser
from cherrypy import tools
from plugins import import_plugin
from geopy.geocoders import Nominatim
from geojson import Feature, Point, FeatureCollection
from geopy.exc import GeocoderTimedOut
from plugins.save.mongo_driver import DBDriver


class API(object):

    def __init__(self):
        self.geolocator = Nominatim()
        self.db_driver = DBDriver()
        self.logger = logging.getLogger("spider.server")
        self.plugins = import_plugin()
        self.config = configparser.ConfigParser()
        self.config.read('../main.py')

    @cherrypy.expose
    @tools.json_out()
    def index(self):
        return {"version": self.config['global']['version'], "tree": ["/", "/data"]}

    @cherrypy.expose
    @tools.json_out()
    def data(self, id=None):
        # cherrypy.response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:4000"
        # for item in db_driver.get():
        #     logger.debug(item)
        if id:
            self.logger.info(self.db_driver.get(ad_id=id))
            return self.db_driver.get(ad_id=id)
        return self.db_driver.get()

    @cherrypy.expose
    @tools.json_out()
    def features(self, choice=None):
        features = list()
        for _ad in self.db_driver.get():
            _feature = _ad['feature']
            _feature['id'] = _ad['id']
            self.logger.info(_feature)
            features.append(_feature)
        return FeatureCollection(features)

    @cherrypy.expose
    @tools.json_out()
    def sync(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:4000"
        ads = []
        for _plug_name, _plugin in self.plugins.items():
            try:
                _ads = _plugin.__driver__.compute()
                # logger.debug(_ads)
                for _ad in _ads:
                    try:
                        _location = self.geolocator.geocode("{}, France".format(_ad['address']))
                        # self.logger.info("address={}".format(_ad['address']))
                        # self.logger.info("_location={}".format(_location))
                        _feature = Feature(geometry=Point((_location.longitude, _location.latitude)))
                    except socket.timeout:
                        self.logger.warning("Timeout during retrieving geocode for {}".format(_ad['address']))
                        _feature = None
                    except GeocoderTimedOut:
                        self.logger.warning("Timeout during retrieving geocode for {}".format(_ad['address']))
                        _feature = None
                    _ad['feature'] = _feature
                    # _feature["ad"] = _ad
                    if self.db_driver.insert(_ad):
                        ads.append(_ad)
            except AttributeError as e:
                self.logger.error('Unable to open plugin {}'.format(_plug_name))
                self.logger.debug(str(e))

        return {"number": len(ads)}
        # return FeatureCollection(ads)

    @cherrypy.expose
    @tools.json_out()
    def purge(self):
        delete_count = self.db_driver.purge()
        return {"number": delete_count}
