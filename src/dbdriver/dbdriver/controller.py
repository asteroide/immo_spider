#!/usr/bin/env python
import pika
import json


class Router:
    def __init__(self):
        pass

    def add(self, data):
        return {"result": "OK", "message": ""}

    def delete(self, data):
        pass

    def list(self, data):
        pass

    def get(self, data):
        pass

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='db_driver')

router = Router()


def on_request(ch, method, props, body):
    print(body.decode("utf-8"))
    request = dict(json.loads(body.decode("utf-8")))

    response = dict()
    if "action" in request:
        if request["action"] == "add":
            response = router.add(request["data"])
        elif request["action"] == "delete":
            response = router.delete(request["data"])
        elif request["action"] == "list":
            response = router.list()
        elif request["action"] == "get":
            response = router.get(request["data"])
        else:
            raise BaseException("Unwknown command {}".format(request["action"]))

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='db_driver')

print(" [x] Awaiting RPC requests")
channel.start_consuming()
