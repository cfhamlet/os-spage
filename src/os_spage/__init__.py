import sys
from spage_reader import SpageReader, read
from spage_writer import SpageWriter, write


def open_file(name, mode, **kwargs):
    def not_support(name, **kwargs):
        raise ValueError, "mode must be 'r' or 'w'"
    r = {'w': SpageWriter, 'r': SpageReader}.get(mode, not_support)
    return r(name, **kwargs)


__all__ = ['__version__', 'version_info', 'open_file']

import pkgutil
__version__ = pkgutil.get_data(__package__, 'VERSION').decode('ascii').strip()
version_info = tuple(int(v) if v.isdigit() else v
                     for v in __version__.split('.'))
del pkgutil
