from cobwebs.mq.core import RPCLink, TopicsLink
from cobwebs.mq.backends.rabbitmq import driver
import pytest
import spider
import json
from unittest import mock

HOST = "127.0.0.1"


def test_driver_instance():
    assert isinstance(driver.rpc, RPCLink)
    assert isinstance(driver.topics, TopicsLink)


@mock.patch("cobwebs.mq.backends.rabbitmq")
def test_rpc(rabbitmq):
    request = {"action": "list", "data": None}
    result = rabbitmq.rpc.send("db_driver", json.dumps(request), HOST)
    rabbitmq.rpc.send.assert_called_with("db_driver", json.dumps(request), HOST)


@mock.patch("cobwebs.mq.backends.rabbitmq")
def test_topic(rabbitmq):
    result = rabbitmq.topic.emit(key="test", message="this is just a message")
    rabbitmq.topic.emit.assert_called_with(key="test",
                                           message="this is just a message")


