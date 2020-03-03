import operator
import sys

PY3 = sys.version_info[0] >= 3

if PY3:
    from io import StringIO as _StringIO
    from io import BytesIO as _BytesIO

    iteritems = operator.methodcaller("items")


else:
    from StringIO import StringIO as _StringIO
    from StringIO import StringIO as _BytesIO

    iteritems = operator.methodcaller("iteritems")

StringIO = _StringIO
BytesIO = _BytesIO
