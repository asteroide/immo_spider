#!/usr/bin/eval PYTHONPATH=/home/asteroide/modules python                                                                                                     

import os
import cherrypy                                                                                                                                               
import logging                                                                                                                                                
import yaml
from api.main import API
from views.main import Views, ManagementArea
from auth import AuthController

from flup.server.fcgi import WSGIServer                                                                                                                       

current_dir = os.path.dirname(os.path.abspath(__file__))
global_config = yaml.load(open("conf.yaml"))

logging.config.dictConfig(global_config['logging'])

logger = logging.getLogger("spider")


class Organizer(object):

    def __init__(self):
        self.api = API()
        self.views = Views()
        self.manager_area = ManagementArea()
        self.auth = AuthController()

    def _cp_dispatch(self, vpath):
        if len(vpath) == 0:
            cherrypy.request.params['name'] = vpath.pop()
            return self.views

        if vpath[0] == "api":
            cherrypy.request.params['name'] = vpath.pop()
            return self.api

        if vpath[0] == "manage":
            cherrypy.request.params['name'] = vpath.pop()
            return self.manager_area

        if vpath[0] == "auth":
            cherrypy.request.params['name'] = vpath.pop()
            return self.auth

        return vpath

application = cherrypy.tree.mount(Organizer(), script_name='/spider.fcgi')

logging.info("Start of server")                                                                                                                               
cherrypy.engine.autoreload.unsubscribe()                                                                                                                      
cherrypy.engine.start()                                                                                                                                       
logging.info("Server started...")                                                                                                                             
                                                                                                                                                              
try:                                                                                                                                                          
    WSGIServer(application).run()                                                                                                                             
finally:                                                                                                                                                      
    cherrypy.engine.stop()                                                                                                                                    
                                                                                                                                                              
