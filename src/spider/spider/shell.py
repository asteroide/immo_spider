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
@click.option("--all", is_flag=True, default=False, help="Delete all item in database")
@click.option("--quickdelete", is_flag=True, default=False, help="Purge all database")
def purge(all, quickdelete):
    if quickdelete:
        logger.info("Purging all...")
        sp = Spider()
        data = sp.purge(quick_delete=True)
        print("action: \033[1mPurging all\033[m")
        print("\t{} items deleted".format(data['data']))
        return
    elif all:
        logger.info("Delete all...")
        sp = Spider()
        data = sp.purge()
    else:
        logger.info("Delete hidden articles...")
        sp = Spider()
        data = sp.purge(hidden=True)
    print("action: \033[1m{}\033[m".format(data["action"]))
    for _key, _value in data["data"].items():
        if _value:
            print("\t{}: \033[32mOK\033[m".format(_key))
        else:
            print("\t{}: \033[31mKO\033[m".format(_key))


@click.command()
@click.argument("ids", nargs=-1)
def hide(ids):
    logger.info("Hiding...")
    sp = Spider()
    data = sp.hide(ids)
    print("action: \033[1m{}\033[m".format(data["action"]))
    for _key, _value in data["data"].items():
        if _value:
            print("\t{}: \033[32mOK\033[m".format(_key))
        else:
            print("\t{}: \033[31mKO\033[m".format(_key))


@click.command()
@click.argument("ids", nargs=-1)
def delete(ids):
    logger.info("Deleting...")
    sp = Spider()
    data = sp.delete(ids)
    print("action: \033[1m{}\033[m".format(data["action"]))
    for _key, _value in data["data"].items():
        if _value:
            print("\t{}: \033[32mOK\033[m".format(_key))
        else:
            print("\t{}: \033[31mKO\033[m".format(_key))


@click.command()
@click.option('--verbose', '-v', default=False, is_flag=True, help='Set verbosity.')
@click.option('--filter', '-f', help='Filter to apply.')
@click.option('--price', '-p', help='Filter on price (ex: 100000:5%).')
@click.option('--garden/--no-garden', help='Filter on the presence of a garden.', default=None)
@click.option('--surface', '-s', help='Filter on surface (ex: 100:5%)')
@click.option('--id', '-i', help='Filter on ID')
def get(verbose=False, filter="", price=None, garden=None, surface=None, id=None):

    sp = Spider()

    _filter = {}
    if filter: _filter["text"] = filter
    if price: _filter["price"] = price
    if garden: _filter["garden"] = garden
    if surface: _filter["surface"] = surface

    for _data in sp.get(req_data={"filter": _filter, "uuid": id}):
        if verbose:
            print("""{id} \033[32m{address:<15} {price:<10} {url}\033[m
\t\033[1mdate :\033[m {date}
\t\033[1msurface :\033[m {surface}
\t\033[1mjardin :\033[m {groundsurface}
\t\033[1mdescription :\033[m {description}
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
            print("{id}\n\t{address:<15} {price:<10} {url}".format(
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
    cli.add_command(hide)
    cli()


if __name__ == "__main__":
    main()
