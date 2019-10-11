import pkgutil
import sys

from .offpage_reader import OffpageReader, read as read_offpage
from .spage_reader import SpageReader, read as read_spage
from .spage_to_offpage import SpageToOffpage, read as spage_to_offpage
from .spage_writer import SpageWriter, write as _write

write = _write


def __not_supported_mode(name, **kwargs):
    raise ValueError("mode must be 'r' or 'w'")


def __not_supported_page_type(name, **kwargs):
    raise ValueError("page_type must be 'spage', 'offpage', 's2o'")


def read(s, page_type="spage"):
    r = {"spage": read_spage, "offpage": read_offpage, "s2o": spage_to_offpage}.get(
        page_type, __not_supported_page_type
    )
    return r(s)


def open_file(name, mode, **kwargs):
    r = {
        "w": SpageWriter,
        "r": {"spage": SpageReader, "offpage": OffpageReader, "s2o": SpageToOffpage},
    }.get(mode, __not_supported_mode)
    if mode == "r":
        r = r.get(kwargs.pop("page_type", "spage"), __not_supported_page_type)

    return r(name, **kwargs)


__all__ = ["__version__", "version_info", "open_file"]

__version__ = pkgutil.get_data(__package__, "VERSION").decode("ascii").strip()
version_info = tuple(int(v) if v.isdigit() else v for v in __version__.split("."))

if sys.version_info < (2, 7):
    sys.exit("os-spage %s requires Python 2.7+" % __version__)

del pkgutil
