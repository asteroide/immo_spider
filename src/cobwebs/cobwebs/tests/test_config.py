from cobwebs.config import get_config, import_plugin


def test_get_config():
    global_config = get_config(confname="conf.yaml", confdir="conf")
    assert isinstance(global_config, dict)
    assert "main" in global_config
    assert "templates" in global_config['main']
    assert "plugins" in global_config['main']
    assert "mq_driver" in global_config['main']
    assert "logging" in global_config


def test_import_plugin():
    global_config = get_config(confname="conf.yaml", confdir="conf")
    plugins = import_plugin(global_config)
    assert isinstance(plugins, tuple)
