import functools
import logging
import pathlib

import requests

from nodc_dyntaxa.dyntaxa_taxon import DyntaxaTaxon
from nodc_dyntaxa.dyntaxa_whitelist import DyntaxaWhitelist
from nodc_dyntaxa.red_list_species import RedListSpecies
from nodc_dyntaxa.translate_dyntaxa import TranslateDyntaxa

logger = logging.getLogger(__name__)

THIS_DIR = pathlib.Path(__file__).parent
CONFIG_DIR = THIS_DIR / 'CONFIG_FILES'

CONFIG_URLS = [
    r'https://raw.githubusercontent.com/nodc-sweden/nodc-dyntaxa/main/src/nodc_dyntaxa/CONFIG_FILES/translate_to_dyntaxa.txt',
    r'https://raw.githubusercontent.com/nodc-sweden/nodc-dyntaxa/main/src/nodc_dyntaxa/CONFIG_FILES/dyntaxa_whitelist.txt',
    r'https://raw.githubusercontent.com/nodc-sweden/nodc-dyntaxa/main/src/nodc_dyntaxa/CONFIG_FILES/Taxon.csv',
    r'https://raw.githubusercontent.com/nodc-sweden/nodc-dyntaxa/main/src/nodc_dyntaxa/CONFIG_FILES/red_list_species.txt',
]


@functools.cache
def get_translate_dyntaxa_object() -> "TranslateDyntaxa":
    path = CONFIG_DIR / "translate_to_dyntaxa.txt"
    return TranslateDyntaxa(path)


@functools.cache
def get_dyntaxa_whitelist_object() -> "DyntaxaWhitelist":
    path = CONFIG_DIR / "dyntaxa_whitelist.txt"
    return DyntaxaWhitelist(path)


@functools.cache
def get_dyntaxa_taxon_object(filter_whitelist=True) -> "DyntaxaTaxon":
    filter_list = None
    if filter_whitelist:
        filter_list = get_dyntaxa_whitelist_object().list
    path = CONFIG_DIR / "Taxon.csv"
    return DyntaxaTaxon(path, filter_list=filter_list)


@functools.cache
def get_red_list_object() -> "RedListSpecies":
    path = CONFIG_DIR / 'red_list_species.txt'
    return RedListSpecies(path)


def update_config_files() -> None:
    """Downloads config files from github"""
    try:
        for url in CONFIG_URLS:
            name = pathlib.Path(url).name
            target_path = CONFIG_DIR / name
            res = requests.get(url)
            with open(target_path, 'w', encoding='utf8') as fid:
                fid.write(res.text)
                logger.info(f'Config file "{name}" updated from {url}')
    except requests.exceptions.ConnectionError:
        logger.warning('Connection error. Could not update config files!')


if __name__ == '__main__':
    update_config_files()


