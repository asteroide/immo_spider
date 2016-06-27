import os
import yaml
import glob
import importlib.machinery
import logging

logger = logging.getLogger("spider.cobwebs")


def get_config(confname="cobwebs.yaml", confdir="."):
    """Try to retrieve the best configuration file

    :param confname: name of the configuration file
    :param confdir: name of the configuration directory
    :return: a dictionary containing the configuration
    """
    _global_config = {}
    for filename in (
        os.path.join(os.getcwd(), ".{}".format(confname)),
        os.path.join(os.getenv("HOME", "/tmp"), ".{}".format(confname)),  # nosec
        "/etc/spider/{}/{}".format(confdir, confname),
        os.path.join(confdir, confname),
    ):
        try:
            _global_config = yaml.safe_load(open(filename))
        except FileNotFoundError:
            continue
    if not _global_config:
        raise BaseException("Could not find a usable configuration file {}/{}".format(confdir, confname))
    return _global_config


def import_plugin(global_config=None):
    if not global_config:
        global_config = get_config()
    plugins = {}
    plugin_list = glob.glob(
        os.path.join(
            global_config["main"]["plugins"],
            "*.py"
        )
    )
    print(plugin_list)
    for _plugin in plugin_list:
        # logger.debug("import_plugin {}".format(_plugin))
        if '__init__' in _plugin:
            continue
        name = os.path.basename(_plugin).split(".")[0]
        plugins[name] = importlib.machinery.SourceFileLoader(name, _plugin).load_module()
    return plugins
