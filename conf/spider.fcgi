#!/usr/bin/eval PYTHONPATH=/home/asteroide/modules python                                                                                                     
                                                                                                                                                              
import cherrypy                                                                                                                                               
import logging                                                                                                                                                
                                                                                                                                                              
from flup.server.fcgi import WSGIServer                                                                                                                       
                                                                                                                                                              
class Main(object):                                                                                                                                           
    @cherrypy.expose                                                                                                                                          
    def index(self):                                                                                                                                          
        return 'Hello World!'                                                                                                                                 
                                                                                                                                                              
application = cherrypy.tree.mount(Main(), script_name='/spider.fcgi')                                                                                         
logging.info("Start of server")                                                                                                                               
cherrypy.engine.autoreload.unsubscribe()                                                                                                                      
cherrypy.engine.start()                                                                                                                                       
logging.info("Server started...")                                                                                                                             
                                                                                                                                                              
try:                                                                                                                                                          
    WSGIServer(application).run()                                                                                                                             
finally:                                                                                                                                                      
    cherrypy.engine.stop()                                                                                                                                    
                                                                                                                                                              
