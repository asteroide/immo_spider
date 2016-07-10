#!/usr/bin/env python3

import sys
from spider import Spider


def help(*args):
    print("""{}

    Commands:
        sync
        get
        help
    """.format(sys.argv[0]))


def sync(*args):
    print("Syncing...")
    sp = Spider()
    sp.sync()


def get(args):
    print("GET: {}".format(args))
    conf_data = {}
    for _data in args:
        key, value = _data.split("=")
        conf_data[key] = value
    sp = Spider()
    print("conf_data={}".format(conf_data))
    for _data in sp.get(conf_data):
        print(_data)
        if not _data["show"]:
            continue
        print("{address:<15} {price:<10} {url}".format(
            address=_data["address"],
            price=_data["price"],
            url=_data["url"]))


commands = (help, sync, get)


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

    print("End")

if __name__ == "__main__":
    main()
