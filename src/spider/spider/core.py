#!/usr/bin/env python3

import json
import importlib
import logging
import socket
from geojson import Feature, Point, FeatureCollection
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from cobwebs.config import get_config, import_plugin

# data_test = {
#     "action": "add",
#     "data": {
#         "address": "test",
#         "description": "",
#         "price": "1000",
#         "date": "",
#         "surface": "",
#         "groundsurface": "",
#         "url": [],
#         "photos": [],
#         "extra": {}
#     }
# }


class Spider:

    def __init__(self):
        self.global_config = get_config()
        driver_module = importlib.import_module(self.global_config['main']['mq_driver'])
        self.mq_driver = driver_module.driver

        self.geolocator = Nominatim()
        self.plugins = import_plugin()
        self.logger = logging.getLogger("spider.api")

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

    def sync(self):
        ads = []
        for _plug_name, _plugin in self.plugins.items():
            try:
                _ads = _plugin.__driver__.compute()
                # self.logger.info('Trying to open plugin {}'.format(_plug_name))
                for _ad in _ads:
                    _ad['feature'] = self.__get_geocode(_ad['address'])
                    request = {"action": "add", "data": _ad}
                    data = mq_driver.rpc.send("db_driver", json.dumps(request), self.global_config['main']['mq_host'])
                    if data:
                        print("sync {}".format(_ad['address']))
                        ads.append(_ad)
            except AttributeError as e:
                self.logger.error('Unable to open plugin {}'.format(_plug_name))
                self.logger.debug(str(e))
                # print('Unable to open plugin {}'.format(_plug_name))

        return {"action": "sync", "number": len(ads), 'message': " ".join(map(lambda x: x['address'], ads))}

    def get(self, uuids):
        if not uuids:
            request = {"action": "list", "data": uuids}
            data = self.mq_driver.rpc.send("db_driver", json.dumps(request), self.global_config['main']['mq_host'])
            for _data in data:
                yield _data
        else:
            for uuid in uuids:
                request = {"action": "get", "data": {"uuid": uuid}}
                data = self.mq_driver.rpc.send("db_driver", json.dumps(request), self.global_config['main']['mq_host'])
                yield data


