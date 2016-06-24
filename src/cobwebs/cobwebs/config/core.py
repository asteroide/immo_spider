import os
import yaml
import glob
import importlib.machinery


def get_config(confname="main.conf", confdir="."):
    """Try to retrieve the best configuration file

    :param confname: name of the configuration file
    :param confdir: name of the configuration directory
    :return: a dictionary containing the configuration
    """
    _global_config = {}
    for filename in (
        os.path.join(os.getcwd(), ".{}".format(confname)),
        os.path.join(os.getenv("HOME", "/tmp"), ".{}".format(confname)),
        "/etc/spider/{}/{}".format(confdir, confname),
        os.path.join(confdir, confname),
    ):
        try:
            print(filename, _global_config)
            _global_config = yaml.load(open(filename))
        except FileNotFoundError:
            pass
    if not _global_config:
        raise BaseException("Could not find a usable configuration file {}/{}".format(confdir, confname))
    return _global_config


def import_plugin():
    plugins = {}
    plugin_list = glob.glob(
        os.path.join(
            get_config()["main"]["plugins"],
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
