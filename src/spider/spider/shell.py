#!/usr/bin/env python3

import sys
import click
from spider import Spider
import cobwebs


logger = cobwebs.getLogger("spider.api")


# def help(*args):
#     print("""{}
#
#     Commands:
#         sync
#         get [filter=...] [uuid=...] [geo_ip=...]
#         purge
#         help
#     """.format(sys.argv[0]))


@click.group()
def cli():
    pass


@click.command()
def sync():
    logger.info("Syncing...")
    sp = Spider()
    sp.sync()


@click.command()
def purge():
    logger.info("Purging...")
    sp = Spider()
    data = sp.purge()
    print(data)


@click.command()
@click.argument("ids", nargs=-1)
def delete(ids):
    logger.info("Deleting...")
    sp = Spider()
    data = sp.delete(ids)
    print("action: \033[1m{}\033[m".format(data["action"]))
    for _key, _value in data["data"].items():
        if _value:
            print("{}: \033[32m{}\033[m".format(_key, _value))
        else:
            print("{}: \033[31m{}\033[m".format(_key, _value))


def __show(filter_str, price=None, garden=None, surface=None, id=None, data=None):
    if not data["show"]:
        return False
    if price:
        if "price" in data and int(data['price']) > 0:
            _prices = []
            if ":" in price:
                _p = price.split(':')
                if "%" in _p[1]:
                    _percent = int(_p[1].replace("%", ""))
                    _prices = [int(_p[0]) * (1 - _percent / 100), int(_p[0]) * (1 + _percent / 100)]
                else:
                    _prices = [int(_p[0]) * (1 - int(_p[0])), int(_p[0]) * (1 + int(_p[0]))]
            else:
                _prices = [int(price), int(price)]
            if _prices[0] > int(data['price']):
                return False
            if int(data['price']) > _prices[1]:
                return False
    if filter_str:
        filter_str = filter_str.lower()
        result = []
        for _filter_str in filter_str.split(","):
            if _filter_str in data["address"].lower():
                result.append(True)
                continue
            if _filter_str in data["description"].lower():
                result.append(True)
                continue
            if _filter_str in data["id"].lower():
                result.append(True)
                continue
            result.append(False)
        if True not in result:
            return False
    if garden is not None:
        if garden == True and "groundsurface" in data:
            if len(data["groundsurface"]) < 0:
                return False
        elif garden == False and "groundsurface" in data:
            if len(data["groundsurface"]) != 0:
                return False
    if surface:
        try:
            _surface = int(data['surface'].replace("m²", ""))
        except ValueError:
            _surface = 0
        if "surface" in data and _surface > 0:
            _surfaces = []
            if ":" in surface:
                _p = surface.split(':')
                if "%" in _p[1]:
                    _percent = int(_p[1].replace("%", ""))
                    _surfaces = [int(_p[0]) * (1 - _percent / 100),
                                 int(_p[0]) * (1 + _percent / 100)]
                else:
                    _surfaces = [int(_p[0]) * (1 - int(_p[0])), int(_p[0]) * (1 + int(_p[0]))]
            else:
                _surfaces = [int(surface), int(surface)]
            if _surfaces[0] > _surface:
                return False
            elif _surface > _surfaces[1]:
                return False
    if id and id != data["id"]:
        return False
    return True


@click.command()
@click.option('--verbose', '-v', default=False, is_flag=True, help='Set verbosity.')
@click.option('--filter', '-f', help='Filter to apply.')
@click.option('--price', '-p', help='Filter on price (ex: 100000:5%).')
@click.option('--garden/--no-garden', help='Filter on the presence of a garden.', default=None)
@click.option('--surface', '-s', help='Filter on surface (ex: 100:5%)')
@click.option('--id', '-i', help='Filter on ID')
def get(verbose=False, filter="", price=None, garden=None, surface=None, id=None):
    # print("GET: {}".format(args))
    # conf_data = {}
    # verbose = False
    # for _data in args:
    #     if _data in ("-v", "--verbose"):
    #         verbose = True
    #         continue
    #     key, value = _data.split("=")
    #     conf_data[key] = value
    sp = Spider()
    # logger.debug("conf_data={}".format(conf_data))
    # _filter = conf_data["filter"] if "filter" in conf_data else None
    for _data in sp.get():
        if not __show(filter, price, garden, surface, id, _data):
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
    cli.add_command(sync)
    cli.add_command(purge)
    cli.add_command(get)
    cli.add_command(delete)
    cli()
    # if len(sys.argv) == 1:
    #     help()
    #     sys.exit(0)
    # else:
    #     for _command in commands:
    #         if _command.__name__ == sys.argv[1].lower():
    #             _command(sys.argv[2:])
    #             break
    #     else:
    #         print("command not found")


if __name__ == "__main__":
    main()
