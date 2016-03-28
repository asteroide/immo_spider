import cherrypy
import logging
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


class Views(object):

    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('main.html')
        return tmpl.render(salutation='Hello', target='World')
