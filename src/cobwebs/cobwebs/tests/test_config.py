from cobwebs.config import get_config


def test_get_config():
    global_config = get_config(confname="main", confdir=".")
    assert isinstance(global_config, dict)
