import cherrypy
import logging
import json
import os
from cherrypy import tools
from plugins import import_plugin
from geopy.geocoders import Nominatim
from geojson import Feature, Point, FeatureCollection
from plugins.save.mongo_driver import DBDriver

VERSION = 0.1

current_dir = os.path.dirname(os.path.abspath(__file__))

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(
    format=FORMAT,
    level=logging.DEBUG)
logger = logging.getLogger("spider.server")

db_driver = DBDriver()
cities = [
    "Vannes",
    "Lorient",
]

geolocator = Nominatim()


class Server(object):

    @cherrypy.expose
    @tools.json_out()
    def index(self):
        return {"version": VERSION, "tree": ["/", "/data"]}

    @cherrypy.expose
    @tools.json_out()
    def data(self, choice=None):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:4000"
        # for item in db_driver.get():
        #     logger.debug(item)
        return FeatureCollection(db_driver.get())

    @cherrypy.expose
    @tools.json_out()
    def sync(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:4000"
        ads = []
        for _plug_name, _plugin in plugins.items():
            try:
                _ads = _plugin.__driver__.compute()
                # logger.debug(_ads)
                for _ad in _ads:
                    _location = geolocator.geocode("{}, France".format(_ad['address']))
                    logger.info("address={}".format(_ad['address']))
                    logger.info("_location={}".format(_location))
                    _feature = Feature(geometry=Point((_location.longitude, _location.latitude)))
                    _feature["ad"] = _ad
                    if db_driver.insert(_feature):
                        ads.append(_feature)
            except AttributeError as e:
                logger.error('Unable to open plugin {}'.format(_plug_name))
                logger.debug(str(e))

        return {"number": len(ads)}
        # return FeatureCollection(ads)

    @cherrypy.expose
    @tools.json_out()
    def purge(self):
        delete_count = db_driver.purge()
        return {"number": delete_count}

plugins = import_plugin()

config = {
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(current_dir, 'static/css')
    },
}
cherrypy.config.update(
    {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
    })
cherrypy.tree.mount(Server(), "", config=config)

if hasattr(cherrypy.engine, 'block'):
    # 3.1 syntax
    cherrypy.engine.start()
    cherrypy.engine.block()
else:
    # 3.0 syntax
    cherrypy.server.quickstart()
    cherrypy.engine.start()
