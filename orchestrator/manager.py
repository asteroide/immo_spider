import cherrypy
import logging
import os
from api.main import API
from views.main import Views

VERSION = 0.1

current_dir = os.path.dirname(os.path.abspath(__file__))

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(
    format=FORMAT,
    level=logging.DEBUG)

cities = [
    "Vannes",
    "Lorient",
]

# config = {
#     '/static': {
#         'tools.staticdir.on': True,
#         'tools.staticdir.dir': os.path.join(current_dir, 'static/css')
#     },
# }
# cherrypy.config.update(
#     {
#         'server.socket_host': '0.0.0.0',
#         'server.socket_port': 8080,
#     })
logger = logging.getLogger("orchestrator")

logger.debug("Using configuration file {}".format(os.path.join(os.getcwd(), "main.conf")))
cherrypy.config.update(os.path.join(os.getcwd(), "main.conf"))

cherrypy.tree.mount(Views(), "/", config=os.path.join(os.getcwd(), "main.conf"))
cherrypy.tree.mount(API(), "/api", config=os.path.join(os.getcwd(), "main.conf"))

# if hasattr(cherrypy.engine, 'block'):
#     # 3.1 syntax
cherrypy.engine.start()
cherrypy.engine.block()
# else:
#     # 3.0 syntax
#     cherrypy.server.quickstart()
#     cherrypy.engine.start()
