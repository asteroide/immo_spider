import cherrypy
import logging
import os
import sys
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
        self.__stop = False
        self.__timer = 60

    def stop(self):
        logger.info("Stop thread...")
        self.__stop = True
        sys.exit(0)

    def run(self):
        cpt = 1
        while True:
            time.sleep(1)
            if self.__stop:
                return
            try:
                if cpt % self.__timer == 0:
                    api.sync()
                    cpt = 0
            except ConnectionError:
                logger.warning("Unable to sync (connection error)...")
            finally:
                cpt += 1



watchdog = WatchDog()
watchdog.start()

current_dir = os.path.dirname(os.path.abspath(__file__))

cities = [
    "Vannes",
    "Lorient",
    "Dinan",
    "Dinard",
    "Lamballe"
]

logger.debug("Using configuration file {}".format(os.path.join(os.getcwd(), "main.conf")))
cherrypy.config.update(os.path.join(os.getcwd(), "main.conf"))

cherrypy.tree.mount(views, "/", config=os.path.join(os.getcwd(), "main.conf"))
cherrypy.tree.mount(api, "/api", config=os.path.join(os.getcwd(), "main.conf"))
cherrypy.tree.mount(auth, "/auth", config=os.path.join(os.getcwd(), "main.conf"))
# cherrypy.engine.signal_handler.subscribe()
cherrypy.engine.signal_handler.set_handler('SIGINT', watchdog.stop)
logger.info("handlers = {}".format(cherrypy.engine.signal_handler.handlers))

try:
    cherrypy.engine.start()
    cherrypy.engine.block()
except KeyboardInterrupt:
    logger.info("Waiting for thread to stop...")
    watchdog.stop()
    # watchdog.join()
