import functools
import logging
import os
import pathlib
import ssl

import requests

from nodc_dyntaxa.dyntaxa_taxon import DyntaxaTaxon
from nodc_dyntaxa.dyntaxa_whitelist import DyntaxaWhitelist
from nodc_dyntaxa.red_list_species import RedListSpecies
from nodc_dyntaxa.translate_dyntaxa import TranslateDyntaxa

logger = logging.getLogger(__name__)

CONFIG_SUBDIRECTORY = 'nodc_dyntaxa'
CONFIG_FILE_NAMES = [
    'translate_to_dyntaxa.txt',
    'dyntaxa_whitelist.txt',
    'Taxon.csv',
    'red_list_species.txt'
]


CONFIG_DIRECTORY = None
if os.getenv('NODC_CONFIG'):
    CONFIG_DIRECTORY = pathlib.Path(os.getenv('NODC_CONFIG')) / CONFIG_SUBDIRECTORY
TEMP_CONFIG_DIRECTORY = pathlib.Path.home() / 'temp_nodc_config' / CONFIG_SUBDIRECTORY


CONFIG_URL = r'https://raw.githubusercontent.com/nodc-sweden/nodc_config/refs/heads/main/' + f'{CONFIG_SUBDIRECTORY}/'


def get_config_path(name: str) -> pathlib.Path:
    if name not in CONFIG_FILE_NAMES:
        raise FileNotFoundError(f'No config file with name "{name}" exists')
    if CONFIG_DIRECTORY:
        path = CONFIG_DIRECTORY / name
        if path.exists():
            return path
    temp_path = TEMP_CONFIG_DIRECTORY / name
    if temp_path.exists():
        return temp_path
    update_config_file(temp_path)
    if temp_path.exists():
        return temp_path
    raise FileNotFoundError(f'Could not find config file {name}')


def update_config_file(path: pathlib.Path) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    url = CONFIG_URL + path.name
    try:
        res = requests.get(url, verify=ssl.CERT_NONE)
        with open(path, 'w', encoding='utf8') as fid:
            fid.write(res.text)
            logger.info(f'Config file "{path.name}" updated from {url}')
    except requests.exceptions.ConnectionError:
        logger.warning(f'Connection error. Could not update config file {path.name}')
        raise


def update_config_files() -> None:
    """Downloads config files from github"""
    for name in CONFIG_FILE_NAMES:
        target_path = TEMP_CONFIG_DIRECTORY / name
        update_config_file(target_path)


@functools.cache
def get_translate_dyntaxa_object() -> "TranslateDyntaxa":
    path = get_config_path("translate_to_dyntaxa.txt")
    return TranslateDyntaxa(path)


@functools.cache
def get_dyntaxa_whitelist_object() -> "DyntaxaWhitelist":
    path = get_config_path("dyntaxa_whitelist.txt")
    return DyntaxaWhitelist(path)


@functools.cache
def get_dyntaxa_taxon_object(filter_whitelist=True) -> "DyntaxaTaxon":
    filter_list = None
    if filter_whitelist:
        filter_list = get_dyntaxa_whitelist_object().list
    path = get_config_path("Taxon.csv")
    print(f'{path=}')
    return DyntaxaTaxon(path, filter_list=filter_list)


@functools.cache
def get_red_list_object() -> "RedListSpecies":
    path = get_config_path('red_list_species.txt')
    return RedListSpecies(path)


if __name__ == '__main__':
    update_config_files()


