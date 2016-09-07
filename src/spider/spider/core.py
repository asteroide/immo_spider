#!/usr/bin/env python3

import json
import importlib
import socket
from geojson import Feature, Point, FeatureCollection
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
import cobwebs
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
        self.logger = cobwebs.getLogger("spider.api")

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
                self.logger.info('Trying to open plugin {}'.format(_plug_name))
                for _ad in _ads:
                    _ad['feature'] = self.__get_geocode(_ad['address'])
                    request = {"action": "add", "data": _ad}
                    data = self.mq_driver.rpc.send("db_driver", json.dumps(request),
                                                   self.global_config['main']['mq_host'])
                    if data:
                        print("sync {}".format(_ad['address']))
                        ads.append(_ad)
            except AttributeError as e:
                self.logger.error('Unable to open plugin {}'.format(_plug_name))
                self.logger.debug(str(e))
                # print('Unable to open plugin {}'.format(_plug_name))

        return {"action": "sync", "number": len(ads), 'message': " ".join(map(lambda x: x['address'], ads))}

    def get(self, req_data=None):
        if not req_data:
            request = {"action": "list", "data": None}
            data = self.mq_driver.rpc.send("db_driver", json.dumps(request), self.global_config['main']['mq_host'])
            for _data in data:
                yield _data
        else:
            request = {"action": "get", "data": req_data}
            data = self.mq_driver.rpc.send("db_driver", json.dumps(request), self.global_config['main']['mq_host'])
            for _data in data:
                yield _data

    def purge(self, only_hidden=False, quick_delete=False):
        if quick_delete:
            request = {"action": "purge", "data": None}
            data = self.mq_driver.rpc.send("db_driver", json.dumps(request), self.global_config['main']['mq_host'])
            request['data'] = data
        elif only_hidden:
            request = {"action": "purge", "data": None}
            ids = {}
            data = self.get()
            for item in data:
                if not item['show']:
                    ret = self.delete((item['id'],))
                    ids[item['id']] = ret['data'][item['id']]
            request['data'] = ids
        else:
            request = {"action": "purge", "data": None}
            ids = {}
            data = self.get()
            for item in data:
                ret = self.delete((item['id'],))
                ids[item['id']] = ret['data'][item['id']]
            request['data'] = ids
        return request

    def delete(self, ids):
        request = {"action": "delete", "data": ids}
        request['data'] = dict()
        for _id in ids:
            _request = dict(request)
            _request['data'] = _id
            data = self.mq_driver.rpc.send("db_driver", json.dumps(_request), self.global_config['main']['mq_host'])
            request['data'][_id] = data
        return request

    def hide(self, ids):
        request = {"action": "hide", "data": ids}
        request['data'] = dict()
        for _id in ids:
            _request = dict(request)
            _request['data'] = _id
            data = self.mq_driver.rpc.send("db_driver", json.dumps(_request), self.global_config['main']['mq_host'])
            request['data'][_id] = data
        return request


