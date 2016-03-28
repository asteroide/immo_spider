import cherrypy
import logging
import json
import os
import configparser
from cherrypy import tools
from plugins import import_plugin
from geopy.geocoders import Nominatim
from geojson import Feature, Point, FeatureCollection
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
    def data(self, choice=None):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:4000"
        # for item in db_driver.get():
        #     logger.debug(item)
        return FeatureCollection(self.db_driver.get())

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
                    _location = self.geolocator.geocode("{}, France".format(_ad['address']))
                    self.logger.info("address={}".format(_ad['address']))
                    self.logger.info("_location={}".format(_location))
                    _feature = Feature(geometry=Point((_location.longitude, _location.latitude)))
                    _feature["ad"] = _ad
                    if self.db_driver.insert(_feature):
                        ads.append(_feature)
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
