import cherrypy
import logging
import socket
import requests
import configparser
import hashlib
from cherrypy import tools
from geopy.geocoders import Nominatim
from geojson import Feature, Point, FeatureCollection
from geopy.exc import GeocoderTimedOut
from spider.auth import AuthController, require
from spider.plugins import import_plugin
from spider.plugins.save.mongo_driver import DBDriver
from spider import __version__

price_colors = (
    # (color, min, max)
    ("#000000", 0, 50000),
    ("#318731", 50001, 90000),
    ("#99ff33", 90001, 120000),
    ("#ffad26", 120001, 150000),
    ("#ff0000", 150001, 200000),
)


class API(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }

    auth = AuthController()

    def __init__(self):
        self.geolocator = Nominatim()
        self.db_driver = DBDriver()
        self.logger = logging.getLogger("spider.api")
        self.plugins = import_plugin()

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

    @staticmethod
    def __get_color_from_price(price):
        if type(price) is not int:
            price = int(price)
        for item in price_colors:
            if item[1] < price < item[2]:
                return item[0]
        return "#000000"

    @cherrypy.expose
    @tools.json_out()
    def index(self):
        return {"version": __version__, "tree": ["/", "/data", "/features"]}

    @cherrypy.expose
    @tools.json_out()
    # @require()
    def data(self, geoid=None, uuid=None, action=None):
        # cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        self.logger.debug("Calling data with {} {} {}".format(geoid, uuid, action))
        if action == "hide":
            self.db_driver.hide(uuid=uuid)
            return
        _items = list()
        if geoid:
            _items = self.db_driver.get(geo_id=geoid)
        elif uuid:
            _items = self.db_driver.get(uuid=uuid)
        else:
            _items = self.db_driver.get()
        for _data in _items:
            color = self.__get_color_from_price(_data['price'])
            _data['color'] = color
        self.logger.debug(_items)
        return _items

    @cherrypy.expose
    @tools.json_out()
    # @require()
    def features(self, choice=None):
        # cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"
        features = list()
        for _ad in self.db_driver.get():
            _feature = _ad['feature']
            color = self.__get_color_from_price(_ad['price'])
            coord = str(_feature['geometry']['coordinates']).encode('utf-8')
            h_coord = hashlib.sha224(coord).hexdigest()
            self.logger.debug("h_coord: {}".format(h_coord))
            self.logger.debug("color: {}".format(color))
            # _feature['id'] = _ad['id']
            _feature['id'] = h_coord
            _feature['color'] = color
            self.logger.info(_feature)
            features.append(_feature)
        return FeatureCollection(features)

    @cherrypy.expose
    @tools.json_out()
    # @require()
    def sync(self):
        # cherrypy.response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:4000"
        ads = []
        for _plug_name, _plugin in self.plugins.items():
            try:
                _ads = _plugin.__driver__.compute()
                self.logger.info('Trying to open plugin {}'.format(_plug_name))
                for _ad in _ads:
                    _ad['feature'] = self.__get_geocode(_ad['address'])
                    if self.db_driver.insert(_ad):
                        ads.append(_ad)
            except AttributeError as e:
                self.logger.error('Unable to open plugin {}'.format(_plug_name))
                self.logger.debug(str(e))

        return {"action": "sync", "number": len(ads), 'message': " ".join(map(lambda x: x['address'], ads))}
        # return FeatureCollection(ads)

    @cherrypy.expose
    @tools.json_out()
    # @require()
    def purge(self):
        delete_count = self.db_driver.purge()
        return {"action": "purge", "number": delete_count}

    @cherrypy.expose
    @tools.json_out()
    # @require()
    def check(self):
        _items = self.db_driver.get()
        results = []
        for _item in _items:
            # self.logger.debug(_item['url'])
            req = requests.get(_item['url'], verify=False)
            if req.status_code not in (200, 201):
                self.logger.warning("Error checking {}".format(_item['url']))
                if self.db_driver.delete(_item['id']):
                    results.append(_item['address'])
        return {"action": "check", "number": len(results), "message": " ".join(results)}
