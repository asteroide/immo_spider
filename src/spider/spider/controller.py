#!/usr/bin/env python
import pika
import uuid
import json


class Controller(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
        self.response = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='db_driver',
                                   properties=pika.BasicProperties(
                                         reply_to=self.callback_queue,
                                         correlation_id=self.corr_id,
                                         ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return json.loads(self.response.decode("utf-8"))

controller = Controller()

print(" [x] Requesting add")

data_test = {
    "action": "add",
    "data": {
        "address": "test",
        "description": "",
        "price": "1000",
        "date": "",
        "surface": "",
        "groundsurface": "",
        "url": [],
        "photos": [],
        "extra": {}
    }
}

response = controller.call(json.dumps(data_test))

print(" [.] Got %r" % response)
