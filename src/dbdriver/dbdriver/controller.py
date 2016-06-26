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
    'url': 'https://www.ouestfrance-immo.com/immobilier/vente/maison/lauzach-56-56109/10696538.htm'
}
"""

import importlib
import hashlib
from pymongo import MongoClient
from cobwebs.config import get_config
from cobwebs.exceptions import AuthException

config = get_config()


class Router:
    def __init__(self, logger):
        self.logger = logger
        # self.logger.emit('logger', "initialization of dbdriver", routing_key='anonymous.info', endpoint='localhost')
        self.client = MongoClient()
        self.spider_db = self.client.spider

    def dispatch(self, ch, method, properties, request):
        response = None
        if "action" in request:
            if request["action"] == "add":
                response = self.add(request["data"])
                # self.logger.emit('logger', "add action", routing_key='dbdriver.info', endpoint='localhost')
            elif request["action"] == "delete":
                response = self.delete(request["data"])
            elif request["action"] == "list":
                response = self.list()
            elif request["action"] == "get":
                response = self.get(request["data"])
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
        if not self.get({'uuid': data['id']}):
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

    def get(self, data=dict()):
        """Get one or more feature

        :param data: a dictionary with the following parameters:
            :param search: a search dictionary
            :param uuid: the ID of an ad
            :param geo_id: the GEOID of an ad
        :return: a list of features
        """
        search = data["search"] if "search" in data else None
        uuid = data["uuid"] if "uuid" in data else None
        geo_id = data["geo_id"] if "geo_id" in data else None
        result = []
        # self.logger.debug("mongo.get geo_id={}".format(geo_id))
        if search:
            return result.append(list(self.spider_db.features.find(search)))
        elif uuid:
            for doc in self.spider_db.features.find():
                if doc['id'] == uuid:
                    doc.pop("_id")
                    result.append(doc)
        elif geo_id:
            for doc in self.spider_db.features.find():
                if "show" in doc and not doc["show"]:
                    continue
                coord = str(doc['feature']['geometry']['coordinates']).encode('utf-8')
                h_coord = hashlib.sha224(coord).hexdigest()
                if h_coord == geo_id:
                    doc.pop("_id")
                    result.append(doc)
        else:
            for doc in self.spider_db.features.find():
                doc.pop("_id")
                result.append(doc)
        # self.logger.debug("mongo.get result={}".format(result))
        return result

    def purge(self):
        """Delete all features in database

        :return: the number of deleted features
        """
        # logger.info("Purging database")
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

    router = Router(mq_driver.topics)

    mq_driver.rpc.run_server('db_driver', router.dispatch, global_config['main']['mq_host'])

if __name__ == "__main__":
    main()
