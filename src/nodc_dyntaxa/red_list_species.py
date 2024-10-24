import logging
import pathlib
import functools

logger = logging.getLogger(__name__)


class RedListSpecies:

    def __init__(self, path: str | pathlib.Path, **kwargs):
        self._path = pathlib.Path(path)
        self._encoding = kwargs.get('encoding', 'utf8')

        self._header = []
        self._data = dict()
        self._synonyms = dict()

        self._load_file()

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def header(self) -> list[str]:
        return self._header

    @property
    def keys(self) -> list[str]:
        return sorted(self._data)

    @property
    def columns_as_keys(self) -> list[str]:
        return ['taxonid', 'svenskt namn', 'vetenskapligt namn']

    @staticmethod
    def _convert_key(key: str) -> str:
        return key.lower().replace(' ', '')

    @staticmethod
    def _convert_header_col(header_col: str) -> str:
        return header_col.strip().lower()

    def _load_file(self) -> None:
        header = []
        with open(self.path, encoding=self._encoding) as fid:
            for r, line in enumerate(fid):
                if not line.strip():
                    continue
                split_line = [item.strip() for item in line.split('\t')]
                if r == 0:
                    self._header = [self._convert_header_col(item) for item in split_line]
                    continue
                line_dict = dict(zip(self.header, split_line))

                for col in self.columns_as_keys:
                    self._data[line_dict[col]] = line_dict

    def get_info(self, key: str = None) -> dict | None:
        return self._data.get(key)

