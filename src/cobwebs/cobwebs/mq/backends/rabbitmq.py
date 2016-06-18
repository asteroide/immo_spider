import json
import pika
import uuid
from cobwebs.mq import Driver, RPCLink, TopicsLink


class RPCRabbitMQ(RPCLink):
    key = None

    def run_server(self, key, callback, endpoint="localhost"):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=endpoint))

        channel = connection.channel()
        channel.queue_declare(queue=key)

        def on_request(ch, method, props, body):
            request = dict(json.loads(body.decode("utf-8")))
            # print("calling callback {}".format(request))
            response = callback(ch, method, props, request)

            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=json.dumps(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(on_request, queue=key)

        print('Awaiting RPC requests')
        channel.start_consuming()

    def send(self, key, data, endpoint):
        self.key = key
        self.__init_client(endpoint)
        return self.__call(data)

    def __init_client(self, endpoint):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=endpoint))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.__on_response, no_ack=True,
                                   queue=self.callback_queue)
        self.response = None

    def __on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def __call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self.key,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return json.loads(self.response.decode("utf-8"))


class TopicsRabbitMQ(TopicsLink):

    def __init__(self):
        self.binding_keys = list("#")
        self.endpoint = 'localhost'
        self.key = None
        self.routing_key = 'anonymous.info'

    @staticmethod
    def run_server(key, binding_keys=list("#"), callback=None, endpoint='localhost'):
        print("TopicsRabbitMQ.run_server {} {} {} {}".format(key, binding_keys, callback, endpoint))
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=endpoint))

        channel = connection.channel()

        channel.exchange_declare(exchange=key,
                                 type='topic')

        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        for binding_key in binding_keys:
            channel.queue_bind(exchange=key,
                               queue=queue_name,
                               routing_key=binding_key)

        channel.basic_consume(callback,
                              queue=queue_name,
                              no_ack=True)

        channel.start_consuming()

    @staticmethod
    def emit(key, message, routing_key='anonymous.info', endpoint='localhost'):
        print("emit {} {} {} {}".format(key, message, routing_key, endpoint))
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=endpoint))

        channel = connection.channel()

        channel.exchange_declare(exchange=key,
                                 type='key')

        channel.basic_publish(exchange=key,
                              routing_key=routing_key,
                              body=message)
        connection.close()

driver = Driver()

driver.rpc = RPCRabbitMQ()
driver.topics = TopicsRabbitMQ()
