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

import logging
import hashlib
from pymongo import MongoClient
from exceptions import AuthException

logger = logging.getLogger("spider.save")


class DBDriver:

    def __init__(self):
        self.client = MongoClient()
        self.spider_db = self.client.spider
        self.logger = logging.getLogger("spider.driver.mongo")

    def insert(self, feature):
        """Insert one feature

        :param feature:
        :return: True if the feature was inserted in the database
        """
        if not self.get(uuid=feature['id']):
            feature['show'] = True
            self.spider_db.features.insert(feature)
            return True
        return False

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

    def get(self, search=None, uuid=None, geo_id=None):
        """Get one or more feature

        :param search: a search dictionary
        :param uuid: the ID of an ad
        :param geo_id: the GEOID of an ad
        :return: a list of features
        """

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
        logger.info("Purging database")
        result = self.spider_db.features.delete_many({})
        return result.deleted_count

    def check_auth(self, username, password):
        user = self.spider_db.auth.find_one({'username': username})
        if user and password == user['password']:
            return True
        raise AuthException()

    def get_user(self):
        users = self.spider_db.auth.find()
        result = []
        for user in users:
            user.pop("password")
            user.pop("_id")
            result.append(user)
        return result

    def add_user(self, username, password):
        user = {
            'username': username,
            'password': hashlib.sha256(password.encode("utf-8")).hexdigest(),
            'role': [],
        }
        self.spider_db.auth.insert_one(user)
        return user

    def del_user(self, usernames):
        for username in usernames:
            if username != 'admin':
                result = self.spider_db.auth.delete_one({'username': username})
                print(username, result.deleted_count)
