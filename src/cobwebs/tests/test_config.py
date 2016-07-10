import os
import tempfile
from unittest import mock
from cobwebs.config import get_config, import_plugin
import pytest


@pytest.fixture(scope="session")
def tmp_config_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp('data').join('conf.yaml')
    open(str(fn), "w").write(str(config_test))
    return str(fn)


def test_get_config(tmp_config_file):
    global_config = get_config(confname=tmp_config_file)
    assert isinstance(global_config, dict)
    assert "main" in global_config
    assert "templates" in global_config['main']
    assert "plugins" in global_config['main']
    assert "mq_driver" in global_config['main']
    assert "logging" in global_config


def test_import_plugin(tmp_config_file):
    global_config = get_config(tmp_config_file)
    plugins = import_plugin(global_config)
    assert isinstance(plugins, dict)


config_test = """main:
  templates: "src/apiviewer/static/templates/"
  plugins: "src/spider/spider/plugins/"
  mq_driver: cobwebs.mq.backends.rabbitmq
  mq_host: localhost

logging:
  version: 1

  formatters:
    brief:
      format: "%(levelname)s %(name)s %(message)-30s"
    custom:
      format: "%(asctime)-15s %(levelname)s %(name)s %(message)s"

  handlers:
    console:
      class : logging.StreamHandler
      formatter: brief
      level   : INFO
      stream  : ext://sys.stdout
    file:
      class : logging.handlers.RotatingFileHandler
      formatter: custom
      level   : DEBUG
      filename: /tmp/logconfig.log
      maxBytes: 1048576
      backupCount: 3

  loggers:
    spider:
      level: DEBUG
      handlers: [file]
      propagate: no

  root:
    level: INFO
    handlers: [file]
"""

#save_config_file()