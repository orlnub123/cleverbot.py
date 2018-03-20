import sys

import pytest


def pytest_ignore_collect(path, config):
    if sys.version_info < (3, 4, 2):
        return True

    if hasattr(config.pluginmanager, 'get_plugin'):
        plugin = config.pluginmanager.get_plugin('asyncio')
    else:
        plugin = config.pluginmanager.getplugin('asyncio')
    if not plugin:
        return True

    import importlib
    if importlib.util.find_spec('aiohttp') is None:
        return True
