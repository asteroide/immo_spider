#!/usr/bin/env python
"""Mongo DB Driver

data = {
    'address': '',
    'date': '21/04/2016',
    'description': '',
    'extra': {'options': ''},
    'feature': {
        'geometry': {
            'coordinates': [-2.5429138, 47.614847],
            'type': 'Point'
        },
        'properties': {},
        'type': 'Feature'
    },
    'groundsurface': '103m²',
    'id': '',
    'price': '97 550\xa0€',
    'surface': '60m²',
    'rooms': 4,
    'bedroom': 3,
    'url': 'https://www.ouestfrance-immo.com/immobilier/vente/maison/lauzach-56-56109/10696538.htm'
}
"""

import re
import logging
import importlib
import hashlib
from pymongo import MongoClient
from cobwebs.config import get_config
from cobwebs.exceptions import AuthException

config = get_config()


def filter_id(function):
    def wrapped(*args, **kwargs):
        result = function(*args, **kwargs)
        _result = []
        for item in result:
            try:
                item.pop("_id")
            except KeyError:
                pass
            _result.append(item)
        return list(_result)
    return wrapped


class Router:
    def __init__(self, logger):
        self.logger = logger
        self.client = MongoClient()
        self.spider_db = self.client.spider

    def dispatch(self, ch, method, properties, request):
        self.logger.debug("dispatch {}".format(request))
        response = None
        if "action" in request:
            if request["action"] == "add":
                response = self.add(request["data"])
                # self.logger.emit('logger', "add action", routing_key='dbdriver.info', endpoint='localhost')
            elif request["action"] == "delete":
                response = self.delete(request["data"])
            elif request["action"] == "hide":
                response = self.hide(request["data"])
            elif request["action"] == "list":
                response = self.list()
            elif request["action"] == "purge":
                response = self.purge()
            elif request["action"] == "get":
                _filter = {}
                _uuid = None
                if "filter" in request["data"]:
                    _filter = request["data"]["filter"]
                if "uuid" in request["data"]:
                    _uuid = request["data"]["uuid"]
                response = self.get(filter=_filter, uuid=_uuid)
            else:
                raise BaseException("Unknown command {}".format(request["action"]))
        else:
            raise BaseException("Cannot understand request {}".format(request))
        return response

    def add(self, data):
        """Insert one feature

        :param feature:
        :return: True if the feature was inserted in the database
        """
        if not self.get(uuid=data['id']):
            data['show'] = True
            self.spider_db.features.insert(data)
            return True
        return False
        # return {"result": "OK", "message": ""}

    def list(self):
        return self.get()

    def delete(self, uuid):
        """Delete one feature

        :param uuid:
        :return: True if the feature was deleted in the database
        """
        result = self.spider_db.features.delete_one({'id': uuid})
        if result.deleted_count == 1:
            return True
        return False

    def hide(self, uuid):
        count = self.spider_db.features.update_one(
            {"id": uuid},
            {"$set": {"show": False}}
        )
        if count.acknowledged:
            return True
        self.logger.error("Cannot find ad with UUID {}".format(uuid))

    def __get_mongo_filter(self, filter):
        _mongo_filter = {"$and": []}
        _mongo_filter_price = {}
        if "show" in filter:
            _mongo_filter["$and"].append({"show": filter["show"]})
        else:
            _mongo_filter["$and"].append({"show": True})
        if "price" in filter:
            _price = re.findall("[\d\.]+", filter['price'])[0]
            try:
                _price = int(_price)
            except ValueError:
                pass
            if ">" in filter['price']:
                _mongo_filter_price['price'] = {"$gt": _price}
            elif "<" in filter['price']:
                _mongo_filter_price['price'] = {"$lt": _price}
            elif ">=" in filter['price']:
                _mongo_filter_price['price'] = {"$gte": _price}
            elif "<=" in filter['price']:
                _mongo_filter_price['price'] = {"$lte": _price}
            elif ":" in filter['price']:
                _p = filter['price'].split(':')
                if "%" in _p[1]:
                    _percent = int(_p[1].replace("%", ""))
                    _prices = [int(_p[0]) * (1 - _percent / 100),
                               int(_p[0]) * (1 + _percent / 100)]
                else:
                    _prices = [int(_p[0]) * (1 - int(_p[0])), int(_p[0]) * (1 + int(_p[0]))]
                _mongo_filter_price['$and'] = [{"price": {"$gte": _prices[0]}},
                                               {"price": {"$lte": _prices[0]}}]
            else:
                _mongo_filter_price['price'] = _price
            _mongo_filter["$and"].append(_mongo_filter_price)
        if "text" in filter:
            _mongo_filter_text = {"$text": {"$search": filter['text']}}
            _mongo_filter["$and"].append(_mongo_filter_text)
        _mongo_filter_surface = {}
        if "surface" in filter:
            _surface = re.findall("[\d\.]+", filter['surface'])[0]
            try:
                _surface = int(_surface)
            except ValueError:
                pass
            if ">" in filter['surface']:
                _mongo_filter_surface['surface'] = {"$gt": _surface}
            elif "<" in filter['surface']:
                _mongo_filter_surface['surface'] = {"$lt": _surface}
            elif ">=" in filter['surface']:
                _mongo_filter_surface['surface'] = {"$gte": _surface}
            elif "<=" in filter['surface']:
                _mongo_filter_surface['surface'] = {"$lte": _surface}
            elif ":" in filter['surface']:
                _p = filter['surface'].split(':')
                if "%" in _p[1]:
                    _percent = int(_p[1].replace("%", ""))
                    _surfaces = [int(_p[0]) * (1 - _percent / 100),
                                 int(_p[0]) * (1 + _percent / 100)]
                else:
                    _surfaces = [int(_p[0]) * (1 - int(_p[0])), int(_p[0]) * (1 + int(_p[0]))]
                _mongo_filter_surface['$and'] = [{"surface": {"$gte": _surfaces[0]}},
                                               {"surface": {"$lte": _surfaces[0]}}]
            else:
                _mongo_filter_surface['surface'] = _surface
            _mongo_filter["$and"].append(_mongo_filter_surface)

        return _mongo_filter

    @filter_id
    def get(self, filter=dict(), uuid=None, geo_id=None):
        """Get one or more feature

        :param filter: a dictionary with the following parameters:
            :param filter: a search dictionary
            :param uuid: the ID of an ad
            :param geo_id: the GEOID of an ad
        :return: a list of features
        """
        self.logger.debug("===> {} {} {}".format(filter, uuid, geo_id))
        if uuid:
            result = []
            for doc in self.spider_db.features.find():
                if doc['id'] == uuid:
                    doc.pop("_id")
                    result.append(doc)
        elif filter:
            _filter = self.__get_mongo_filter(filter)
            result = self.spider_db.features.find(_filter)
        elif geo_id:
            result = []
            for doc in self.spider_db.features.find():
                if "show" in doc and not doc["show"]:
                    continue
                coord = str(doc['feature']['geometry']['coordinates']).encode('utf-8')
                h_coord = hashlib.sha224(coord).hexdigest()
                if h_coord == geo_id:
                    doc.pop("_id")
                    result.append(doc)
        else:
            result = []
            for doc in self.spider_db.features.find():
                doc.pop("_id")
                result.append(doc)
        return result

    def purge(self):
        """Delete all features in database

        :return: the number of deleted features
        """
        self.logger.info("Purging database")
        result = self.spider_db.features.delete_many({})
        return result.deleted_count

    def check_auth(self, username, password):
        user = self.spider_db.auth.find_one({'username': username})
        if user and password == user['password']:  # nosec (not a hardcoded password)
            return True
        raise AuthException()

    def get_user(self):
        users = self.spider_db.auth.find()
        result = []
        for user in users:
            user.pop("password")  # nosec (not a hardcoded password)
            user.pop("_id")
            result.append(user)
        return result

    def add_user(self, username, password):
        user = {
            'username': username,
            'password': hashlib.sha256(password.encode("utf-8")).hexdigest(),  # nosec (not a hardcoded password)
            'role': [],
        }
        self.spider_db.auth.insert_one(user)
        return user

    def del_user(self, usernames):
        for username in usernames:
            if username != 'admin':  # nosec (not a hardcoded password)
                result = self.spider_db.auth.delete_one({'username': username})
                print(username, result.deleted_count)


def main():
    global_config = get_config()

    driver_module = importlib.import_module(global_config['main']['mq_driver'])
    mq_driver = driver_module.driver

    logger = logging.getLogger("spider.dbdriver")
    router = Router(logger)

    mq_driver.rpc.run_server('db_driver', router.dispatch, global_config['main']['mq_host'])

if __name__ == "__main__":
    main()
