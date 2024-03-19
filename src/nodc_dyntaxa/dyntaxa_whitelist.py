import logging
import pathlib

logger = logging.getLogger(__name__)


class DyntaxaWhitelist:
    species_key = 'scientific_name'

    def __init__(self, path: str | pathlib.Path, **kwargs):
        self._path = pathlib.Path(path)
        self._encoding = kwargs.get('encoding', 'cp1252')

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
    def list(self) -> list[str]:
        return sorted(self._data)

    @staticmethod
    def _convert_key(key: str) -> str:
        return key.lower().replace(' ', '')

    def _load_file(self) -> None:
        ranks = set()
        with open(self.path) as fid:
            for r, line in enumerate(fid):
                if not line.strip():
                    continue
                split_line = [item.strip() for item in line.split('\t')]
                if r == 0:
                    self._header = split_line
                    continue
                line_dict = dict(zip(self.header, split_line))
                ranks.add(line_dict['rank'])
                self._data[self._convert_key(line_dict[self.species_key])] = line_dict

    def get(self, key: str = None) -> str | bool:
        """Returns the given scientific_name if present in the whitelist. Else returns False."""
        info = self._data.get(self._convert_key(key), None)
        if not info:
            return False
        return info[self.species_key]



