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
        if not self.get(ad_id=feature['id']):
            self.spider_db.features.insert(feature)
            return True
        return False

    def get(self, search=None, ad_id=None, geo_id=None):
        """Get one or more feature

        :param search: a search dictionary
        :param ad_id: the ID of an ad
        :return: a list of features
        """

        result = []
        # self.logger.debug("mongo.get geo_id={}".format(geo_id))
        if search:
            return result.append(list(self.spider_db.features.find(search)))
        elif ad_id:
            for doc in self.spider_db.features.find():
                if doc['id'] == ad_id:
                    doc.pop("_id")
                    result.append(doc)
        elif geo_id:
            for doc in self.spider_db.features.find():
                # self.logger.debug("mongo.get doc={}".format(doc['id']))
                coord = str(doc['feature']['geometry']['coordinates']).encode('utf-8')
                h_coord = hashlib.sha224(coord).hexdigest()
                if h_coord == geo_id:
                    doc.pop("_id")
                    result.append(doc)
        else:
            for doc in self.spider_db.features.find():
                doc.pop("_id")
                result.append(doc)
        self.logger.debug("mongo.get result={}".format(result))
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
