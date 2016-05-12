class driver(object):

    data_template = {
        "address": "",
        "description": "",
        "price": "",
        "date": "",
        "surface": "",
        "groundsurface": "",
        "url": [],
        "photos": [],
        "extra": {},
    }

    def compute(self, city_name, area=30):
        """Retrieve specific data for that plugin

        :param city_name: name of the city
        :param area: maximal area to search for data
        :return:
        """
        raise NotImplemented
