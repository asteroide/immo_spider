import sys
# sys.stdout = sys.stderr
import os

import atexit
import threading
import cherrypy
import yaml
import logging
import logging.config
from spider.api.main import API
from spider.views.main import Views, ManagementArea
from spider.auth import AuthController

cherrypy.config.update({
    'environment': 'embedded',
    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    'tools.sessions.on': True,
    'tools.sessions.storage_type': "file",
    'tools.sessions.storage_path': "/tmp/sessions",
    'tools.sessions.timeout': 60
})
global_config = yaml.load(open("/vagrant/conf/conf.yaml"))

logging.config.dictConfig(global_config['logging'])

logger = logging.getLogger("spider")

# hooks.attach('before_finalize', _sessions.save)
# hooks.attach('on_end_request', _sessions.close)

views = Views()
views.api = API()
views.auth = AuthController()
views.manage = ManagementArea()

application = cherrypy.Application(views, script_name=None, config=None)
