import cherrypy
import logging
from jinja2 import Environment, FileSystemLoader
from auth import require, AuthController, member_of
from plugins.save.mongo_driver import DBDriver

env = Environment(loader=FileSystemLoader('templates'))


class Views(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True
    }
    auth = AuthController()

    def __init__(self):
        self.logger = logging.getLogger("spider.views")
        self.logger.debug("Views {}".format(self._cp_config))

    @cherrypy.expose
    @require()
    def index(self):
        tmpl = env.get_template('main.html')
        return tmpl.render()


class ManagementArea(object):

    db_driver = DBDriver()

    _cp_config = {
        'auth.require': [member_of('admin')],
        'tools.sessions.on': True,
        'tools.auth.on': True
    }
    auth = AuthController()

    def __init__(self):
        self.logger = logging.getLogger("spider.views")
        self.logger.debug("ManagementArea {}".format(self._cp_config))

    @cherrypy.expose
    @require()
    def index(self, username=None, password1=None, password2=None, check=None):
        if cherrypy.request.method == "POST":
            if username and password1 and password2 and password1 == password2:
                self.db_driver.add_user(username, password1)
            elif check:
                if type(check) is str:
                    check = [check, ]
                self.db_driver.del_user(check)
        tmpl = env.get_template('manage.html')
        return tmpl.render(users=self.db_driver.get_user())


