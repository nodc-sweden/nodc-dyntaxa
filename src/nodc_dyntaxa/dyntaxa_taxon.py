import pathlib

import polars as pl
import functools


class DyntaxaTaxon:
    first_col = 'taxonId'

    def __init__(self, path: str | pathlib.Path, filter_list: list[str] | None = None):
        self._path = pathlib.Path(path)
        self._filter_list = filter_list
        self._df: pl.DataFrame | None = None
        self._remove_bad_chars_in_file()
        self._load_file()
        self._cleanup_data()

    @property
    def all_taxon_ranks(self) -> list[str]:
        return list(self._df['taxonRank'].unique())

    def _remove_bad_chars_in_file(self) -> None:
        with open(self._path, encoding='utf8') as fid:
            data = fid.read()
        data = data.replace('"', '<>')
        with open(self._path, 'w', encoding='utf8') as fid:
            fid.write(data)

    def _load_file(self) -> None:
        self._df = pl.read_csv(self._path, separator='\t', encoding='utf8', infer_schema_length=int(1e10), ignore_errors=True, schema_overrides={'taxonRemarks': str})

    def _cleanup_data(self) -> None:
        self._df = self._df.filter(~pl.col(self.first_col).str.starts_with('#'))
        # self._df = self._df.filter(pl.col('taxonomicStatus').eq('accepted'))
        self._df = self._df.with_columns(
            pl.col('taxonId').map_elements(lambda x: x.split(':')[-1].strip(), return_dtype=str).alias('taxon_id'))

        self._df = self._df.with_columns(
            pl.col('taxonId').map_elements(lambda x: x.split(':')[-2].strip(), return_dtype=str).alias('taxon_id_tag'))

        self._df = self._df.with_columns(
            pl.col('acceptedNameUsageID').map_elements(lambda x: x.split(':')[-1].strip(), return_dtype=str).alias('accepted_taxon_id'))

        self._df = self._df.with_columns(
            pl.col('parentNameUsageID').map_elements(lambda x: x.split(':')[-1].strip(), return_dtype=str).alias('parent_taxon_id'))

        if self._filter_list:
            self._df.filter(pl.col('scientificName').str.to_lowercase().is_in(self._filter_list))
    
    @functools.cache
    def get(self, name: str) -> str | bool:
        """Returns taxon_id for the given scientific name. Status must be accepted. Returns False if no match found."""
        try:
            result = self._df.filter(pl.col('scientificName') == name, pl.col('taxonomicStatus') == 'accepted')
            if result.is_empty():
                return False
            return result['accepted_taxon_id'][0]
            # return self._df.row(by_predicate=(pl.col('scientificName') == name), named=True)['taxon_id']
        except pl.exceptions.NoRowsReturnedError:
            return False

    def old_get_info(self, **kwargs) -> dict | list[dict] | bool:
        """Returns information from trophic type list filtered on data in kwargs"""
        data = self._df.filter(**kwargs).to_dict(as_series=False)
        info = []
        for i in range(len(data[self.first_col])):
            info.append(dict((key, data[key][i]) for key in data))
        if len(info) == 1:
            return info[0]
        return info

    def get_info(self, **kwargs) -> dict | list[dict] | bool:
        """Returns information from trophic type list filtered on data in kwargs"""
        data = self._df.filter(**kwargs).to_dicts()
        data_with_parent_ranks = []
        for d in data:
            d['taxon_hierarchy_list'] = [d['scientificName']]
            self._add_parent_taxon_rank(d, d['parent_taxon_id'])
            d['taxon_hierarchy'] = ' - '.join(reversed(d['taxon_hierarchy_list']))
            data_with_parent_ranks.append(d)
        return data_with_parent_ranks

    def _add_parent_taxon_rank(self, data: dict, taxon_id: str) -> None:
        if not taxon_id:
            return
        parent_data = self._df.filter(taxon_id=taxon_id).to_dicts()
        # parent_data = self._df.filter(taxon_id=taxon_id, taxon_id_tag='Taxon').to_dicts()
        if len(parent_data) != 1:
            raise Exception(f'Found several parent ids for dyntaxa id {taxon_id} ')
        pdata = parent_data[0]
        data['taxon_hierarchy_list'].append(pdata['scientificName'])
        data[pdata['taxonRank']] = pdata['scientificName']
        self._add_parent_taxon_rank(data, pdata['parent_taxon_id'])

