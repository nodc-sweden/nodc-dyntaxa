import pathlib

from nodc_config import Config

from nodc_dyntaxa.dyntaxa_taxon import DyntaxaTaxon
from nodc_dyntaxa.dyntaxa_whitelist import DyntaxaWhitelist
from nodc_dyntaxa.red_list_species import RedListSpecies
from nodc_dyntaxa.translate_dyntaxa import TranslateDyntaxa


def get_config_path(nodc_conf: Config, name: str) -> pathlib.Path:
    path = nodc_conf.get_path(name)
    if path is None:
        raise FileNotFoundError(f"nodc-config path '{name}' not found")
    return path


def get_translate_dyntaxa_object(nodc_conf: Config) -> TranslateDyntaxa:
    path = get_config_path(nodc_conf, "translate_to_dyntaxa.txt")
    return TranslateDyntaxa(path)


def get_dyntaxa_whitelist_object(nodc_conf: Config) -> DyntaxaWhitelist:
    path = get_config_path(nodc_conf, "dyntaxa_whitelist.txt")
    return DyntaxaWhitelist(path)


def get_dyntaxa_taxon_object(
    nodc_conf: Config, filter_whitelist: bool = True
) -> DyntaxaTaxon:
    filter_list = None
    if filter_whitelist:
        filter_list = get_dyntaxa_whitelist_object(nodc_conf).list
    path = get_config_path(nodc_conf, "Taxon.csv")
    return DyntaxaTaxon(path, filter_list=filter_list)


def get_red_list_object(nodc_conf: Config) -> RedListSpecies:
    path = get_config_path(nodc_conf, "red_list_species.txt")
    return RedListSpecies(path)
