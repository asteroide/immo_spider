import cherrypy
import logging
import os
from api.main import API
from views.main import Views
from auth import AuthController
import threading
import time
from requests.exceptions import ConnectionError

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(
    format=FORMAT,
    level=logging.DEBUG)

logger = logging.getLogger("orchestrator")


api = API()
views = Views()
auth = AuthController()


class WatchDog(threading.Thread):

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)

    def run(self):
        # TODO: add a thread killer
        while True:
            time.sleep(60)
            try:
                api.sync()
            except ConnectionError:
                logger.warning("Unable to sync (connection error)...")


watchdog = WatchDog()
watchdog.start()

current_dir = os.path.dirname(os.path.abspath(__file__))

cities = [
    "Vannes",
    "Lorient",
]

logger.debug("Using configuration file {}".format(os.path.join(os.getcwd(), "main.conf")))
cherrypy.config.update(os.path.join(os.getcwd(), "main.conf"))

cherrypy.tree.mount(views, "/", config=os.path.join(os.getcwd(), "main.conf"))
cherrypy.tree.mount(api, "/api", config=os.path.join(os.getcwd(), "main.conf"))
cherrypy.tree.mount(auth, "/auth", config=os.path.join(os.getcwd(), "main.conf"))

cherrypy.engine.start()
cherrypy.engine.block()
watchdog.join()
