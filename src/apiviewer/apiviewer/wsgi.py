from flask import Flask
from flask_restful import Resource, Api, reqparse
from apiviewer import __version__
import json
import importlib
from cobwebs.config import get_config

global_config = get_config()

driver_module = importlib.import_module(global_config['main']['mq_driver'])
mq_driver = driver_module.driver


app = Flask(__name__)
api = Api(app)

# parser = reqparse.RequestParser()
# parser.add_argument('action', type=str, help="Action to be performed on data")
# parser.add_argument('uuid', type=str, help="UUID of the object")


class Root(Resource):

    def get(self):
        class_objects = (Root, Data, Features)
        methods = ("get", "post", "put", "head", "delete", "options")
        tree = {}
        for co in class_objects:
            url = "/" + co.__name__.lower()
            if co.__name__.lower() == "root":
                url = "/"
            tree[url] = {}
            tree[url]["methods"] = list(filter(lambda x: x in dir(co), methods))
            description = co.__doc__ or ""
            tree[url]["description"] = description.strip()
        return {"version": __version__, "tree": tree}


class Data(Resource):
    """
    Endpoint to retrieve, synchronize or delete all data
    """

    def get(self, uuid=None):
        """

        :param uuid:
        :return:
        """
        if not uuid:
            request = {"action": "list", "data": None}
        else:
            request = {"action": "get", "data": {"uuid": uuid}}
        data = mq_driver.rpc.send("db_driver", json.dumps(request), global_config['main']['mq_host'])
        return {'action': "list", "length": len(data), "data": data}

    def post(self, uuid=None):
        """
        Force synchronising the spider
        :param uuid: not used here
        :return: JSON object representing the result of the synchronisation
        """
        # args = parser.parse_args()
        # TODO
        return {'uuid': uuid}

    def delete(self, uuid):
        """
        Delete a data object given its UUID
        :param uuid:
        :return:
        """
        # args = parser.parse_args()
        # TODO
        return {'uuid': uuid}


class Features(Resource):
    """
    Endpoint to only retrieve features
    """

    def get(self):
        return {'hello': 'world'}


api.add_resource(Root, '/')
api.add_resource(Data, '/data', '/data/', '/data/<string:uuid>')
api.add_resource(Features, '/features')


def main():
    app.run(debug=True, host="0.0.0.0", port=4000)

if __name__ == '__main__':
    main()
