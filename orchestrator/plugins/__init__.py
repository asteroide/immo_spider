import importlib
import glob
import os


def import_plugin():
    plugins = {}
    plugin_list = glob.glob("plugins/compute/*.py")
    for _plugin in plugin_list:
        if '__init__' in _plugin:
            continue
        name = os.path.basename(_plugin).split(".")[0]
        plugin_id = _plugin.replace(".py", "").replace("/", ".")
        plugins[name] = importlib.import_module(plugin_id)
    return plugins

