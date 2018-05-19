"""Pull data from geth and parse it into mongo."""
import logging
import subprocess

import click

from ethex.analysis.contract_map import ContractMap
from ethex.crawler.crawler import Crawler
from ethex.structure import PATH

@click.group()
def cli():
    pass


@cli.command()
def preprocess():
    subprocess.call([
        "(geth --rpc --rpcport 8545 > {}/geth.log 2>&1) &".format(PATH['LOGDIR']),
        "(mongod --dbpath mongo/data --port 27017 > {}/mongo.log 2>&1) &"
            .format(PATH['LOGDIR'])
    ], shell=True)

    logging.info("Booting processes.")
    # Catch up with the crawler
    c = Crawler()

    logging.info("Updating contract hash map.")
    # Update the contract addresses that have been interacted with
    ContractMap(c.mongo_client, last_block=c.max_block_mongo)

    logging.info("Update complete.")
    subprocess.call([
        "(geth --rpc --rpcport 8545 > {}/geth.log 2>&1) &".format(LOGDIR),
        "(mongod --dbpath mongo/data --port 27017 > {}/mongo.log 2>&1) &".format(LOGDIR)
    ], shell=True)


if __name__ == '__main__':
    cli()