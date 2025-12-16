import functools
import logging
import os
import pathlib

from nodc_dyntaxa.dyntaxa_taxon import DyntaxaTaxon
from nodc_dyntaxa.dyntaxa_whitelist import DyntaxaWhitelist
from nodc_dyntaxa.red_list_species import RedListSpecies
from nodc_dyntaxa.translate_dyntaxa import TranslateDyntaxa


def get_user_given_config_dir() -> pathlib.Path | None:
    path = pathlib.Path(os.getcwd()) / "config_directory.txt"
    if not path.exists():
        return
    with open(path) as fid:
        config_path = fid.readline().strip()
        if not config_path:
            return
        config_path = pathlib.Path(config_path)
        if not config_path.exists():
            return
        return config_path


logger = logging.getLogger(__name__)

CONFIG_ENV = "NODC_CONFIG"

home = pathlib.Path.home()
OTHER_CONFIG_SOURCES = [
    home / "NODC_CONFIG",
    home / ".NODC_CONFIG",
    home / "nodc_config",
    home / ".nodc_config",
]

CONFIG_FILE_NAMES = [
    "translate_to_dyntaxa.txt",
    "dyntaxa_whitelist.txt",
    "Taxon.csv",
    "red_list_species.txt",
]


CONFIG_DIRECTORY = None
conf_dir = get_user_given_config_dir()
if conf_dir:
    CONFIG_DIRECTORY = conf_dir
else:
    if os.getenv(CONFIG_ENV) and pathlib.Path(os.getenv(CONFIG_ENV)).exists():
        CONFIG_DIRECTORY = pathlib.Path(os.getenv(CONFIG_ENV))
    else:
        for directory in OTHER_CONFIG_SOURCES:
            if directory.exists():
                CONFIG_DIRECTORY = directory
                break


def get_config_path(name: str, subdir: str = None) -> pathlib.Path:
    if not CONFIG_DIRECTORY:
        raise NotADirectoryError(
            f"Config directory not found. Environment path {CONFIG_ENV} does not seem to be set and not other config directory was found. "
        )

    if name not in CONFIG_FILE_NAMES:
        raise FileNotFoundError(f'No config file with name "{name}" exists')
    root = CONFIG_DIRECTORY
    if subdir:
        root = root / subdir
    path = root / name
    if not path.exists():
        raise FileNotFoundError(f"Could not find config file {name}")
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
    path = get_config_path("Taxon.csv", subdir="dyntaxa_dwca")
    return DyntaxaTaxon(path, filter_list=filter_list)


@functools.cache
def get_red_list_object() -> "RedListSpecies":
    path = get_config_path("red_list_species.txt")
    return RedListSpecies(path)


if __name__ == "__main__":
    tran = get_translate_dyntaxa_object()
    white = get_dyntaxa_whitelist_object()
    taxon = get_dyntaxa_taxon_object()
    red = get_red_list_object()
