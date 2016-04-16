import cherrypy
import logging
from jinja2 import Environment, FileSystemLoader
from auth import require, AuthController

env = Environment(loader=FileSystemLoader('templates'))


class Views(object):

    auth = AuthController()

    @cherrypy.expose
    @require()
    def index(self):
        tmpl = env.get_template('main.html')
        return tmpl.render()
