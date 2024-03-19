import functools
import pathlib
import sys

from .dyntaxa_taxon import DyntaxaTaxon
from .dyntaxa_whitelist import DyntaxaWhitelist
from .translate_dyntaxa import TranslateDyntaxa
from .red_list_species import RedListSpecies


if getattr(sys, 'frozen', False):
    THIS_DIR = pathlib.Path(sys.executable).parent
else:
    THIS_DIR = pathlib.Path(__file__).parent

CONFIG_DIR = THIS_DIR / 'CONFIG_FILES'


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
