#!/usr/bin/env python3

import sys
from spider import Spider
import cobwebs


logger = cobwebs.getLogger("spider.api")


def help(*args):
    print("""{}

    Commands:
        sync
        get [filter=...] [uuid=...] [geo_ip=...]
        purge
        help
    """.format(sys.argv[0]))


def sync(*args):
    logger.info("Syncing...")
    sp = Spider()
    sp.sync()


def purge(*args):
    logger.info("Purging...")
    sp = Spider()
    data = sp.purge()
    print(data)


def __show(filter_str, data):
    if not data["show"]:
        return False
    if filter_str:
        print("if filter_str")
        for _filter_str in filter_str.split(","):
            if _filter_str in data["address"]:
                return True
            if _filter_str in data["description"]:
                return True
            if _filter_str in data["id"]:
                return True
        return False
    return True


def get(args):
    # print("GET: {}".format(args))
    conf_data = {}
    verbose = False
    for _data in args:
        if _data in ("-v", "--verbose"):
            verbose = True
            continue
        key, value = _data.split("=")
        conf_data[key] = value
    sp = Spider()
    logger.debug("conf_data={}".format(conf_data))
    _filter = conf_data["filter"] if "filter" in conf_data else None
    for _data in sp.get(conf_data):
        if not __show(_filter, _data):
            continue
        # if not _data["show"]:
        #     continue
        # if "filter" in conf_data:
        #     if conf_data["filter"] not in _data["address"] and \
        #                     conf_data["filter"] not in _data["description"]:
        #         continue
        # print(_data.keys())
        if verbose:
            print("""{id} \033[32m{address:<15} {price:<10} {url}\033[m
\033[1mdate :\033[m {date}
\033[1msurface :\033[m {surface}
\033[1mjardin :\033[m {groundsurface}
\033[1mdescription :\033[m {description}
            """.format(
                id=_data["id"],
                address=_data["address"],
                price=_data["price"],
                url=_data["url"],
                date=_data["date"],
                surface=_data["surface"],
                groundsurface=_data["groundsurface"],
                description=_data["description"].strip(),
            ))
        else:
            print("{id}\n{address:<15} {price:<10} {url}".format(
                id=_data["id"],
                address=_data["address"],
                price=_data["price"],
                url=_data["url"]))


commands = (help, sync, get, purge)


def main():
    if len(sys.argv) == 1:
        help()
        sys.exit(0)
    else:
        for _command in commands:
            if _command.__name__ == sys.argv[1].lower():
                _command(sys.argv[2:])
                break
        else:
            print("command not found")


if __name__ == "__main__":
    main()
