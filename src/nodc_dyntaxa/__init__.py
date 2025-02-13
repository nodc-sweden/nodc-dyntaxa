import functools
import logging
import os
import pathlib

from nodc_dyntaxa.dyntaxa_taxon import DyntaxaTaxon
from nodc_dyntaxa.dyntaxa_whitelist import DyntaxaWhitelist
from nodc_dyntaxa.red_list_species import RedListSpecies
from nodc_dyntaxa.translate_dyntaxa import TranslateDyntaxa

logger = logging.getLogger(__name__)

CONFIG_ENV = 'NODC_CONFIG'

CONFIG_FILE_NAMES = [
    'translate_to_dyntaxa.txt',
    'dyntaxa_whitelist.txt',
    'Taxon.csv',
    'red_list_species.txt'
]


CONFIG_DIRECTORY = None
if os.getenv(CONFIG_ENV) and pathlib.Path(os.getenv(CONFIG_ENV)).exists():
    CONFIG_DIRECTORY = pathlib.Path(os.getenv(CONFIG_ENV))


def get_config_path(name: str) -> pathlib.Path:
    if not CONFIG_DIRECTORY:
        raise NotADirectoryError(f'Config directory not found. Environment path {CONFIG_ENV} does not seem to be set.')
    if name not in CONFIG_FILE_NAMES:
        raise FileNotFoundError(f'No config file with name "{name}" exists')
    path = CONFIG_DIRECTORY / name
    if not path.exists():
        raise FileNotFoundError(f'Could not find config file {name}')
    return path


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
    return DyntaxaTaxon(path, filter_list=filter_list)


@functools.cache
def get_red_list_object() -> "RedListSpecies":
    path = get_config_path('red_list_species.txt')
    return RedListSpecies(path)


if __name__ == '__main__':
    tran = get_translate_dyntaxa_object()
    white = get_dyntaxa_whitelist_object()
    taxon = get_dyntaxa_taxon_object()
    red = get_red_list_object()


