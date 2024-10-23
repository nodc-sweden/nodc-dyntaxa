import pathlib

import polars as pl
import functools


class DyntaxaTaxon:
    first_col = 'taxonId'

    def __init__(self, path: str | pathlib.Path, filter_list: list[str] | None = None):
        self._path = pathlib.Path(path)
        self._filter_list = filter_list
        self._df: pl.DataFrame | None = None
        self._load_file()
        self._cleanup_data()

    def _load_file(self) -> None:
        self._df = pl.read_csv(self._path, separator='\t')

    def _cleanup_data(self) -> None:
        self._df = self._df.filter(~pl.col(self.first_col).str.starts_with('#'))
        self._df = self._df.with_columns(pl.col('taxonId').map_elements(lambda x: x.split(':')[-1].strip(), return_dtype=str).alias(
            'taxon_id'))
        if self._filter_list:
            self._df.filter(pl.col('scientificName').str.to_lowercase().is_in(self._filter_list))
    
    @functools.cache
    def get(self, name: str) -> str | bool:
        """Returns taxon_id for the given scientific name. Status must be accepted. Returns False if no match found."""
        try:
            result = self._df.filter(pl.col('scientificName') == name, pl.col('taxonomicStatus') == 'accepted')
            if result.is_empty():
                return False
            return result['taxon_id'][0]
            # return self._df.row(by_predicate=(pl.col('scientificName') == name), named=True)['taxon_id']
        except pl.exceptions.NoRowsReturnedError:
            return False

    def get_info(self, **kwargs) -> dict | list[dict] | bool:
        """Returns information from trophic type list filtered on data in kwargs"""
        data = self._df.filter(**kwargs).to_dict(as_series=False)
        info = []
        for i in range(len(data[self.first_col])):
            info.append(dict((key, data[key][i]) for key in data))
        if len(info) == 1:
            return info[0]
        return info
