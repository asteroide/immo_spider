import importlib
import glob
import os
import importlib.machinery
from spider import __global_config__
import logging

logger = logging.getLogger("spider.init")


def import_plugin():
    plugins = {}
    plugin_list = glob.glob(
        os.path.join(
            __global_config__["main"]["plugins"],
            "compute",
            "*.py"
        )
    )
    for _plugin in plugin_list:
        logger.debug("import_plugin {}".format(_plugin))
        if '__init__' in _plugin:
            continue
        name = os.path.basename(_plugin).split(".")[0]
        plugins[name] = importlib.machinery.SourceFileLoader(name, _plugin).load_module()
    return plugins

