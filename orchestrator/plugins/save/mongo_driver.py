import logging
from pymongo import MongoClient


logger = logging.getLogger("spider.save")


class DBDriver:

    def __init__(self):
        self.client = MongoClient()
        self.spider_db = self.client.spider

    def insert(self, feature):
        """Insert one feature

        :param feature:
        :return: True if the feature was inserted in the database
        """
        if not self.get(ad_id=feature['id']):
            self.spider_db.features.insert(feature)
            return True
        return False

    def get(self, search=None, ad_id=None):
        """Get one or more feature

        :param search: a search dictionary
        :param ad_id: the ID of an ad
        :return: a list of features
        """

        result = []
        if search:
            return result.append(list(self.spider_db.features.find(search)))
        elif ad_id:
            for doc in self.spider_db.features.find():
                if doc['id'] == ad_id:
                    doc.pop("_id")
                    return doc
        else:
            for doc in self.spider_db.features.find():
                doc.pop("_id")
                result.append(doc)
        return result

    def purge(self):
        """Delete all features in database

        :return: the number of deleted features
        """
        logger.info("Purging database")
        result = self.spider_db.features.delete_many({})
        return result.deleted_count

