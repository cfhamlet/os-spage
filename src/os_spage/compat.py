import sys
import operator

PY3 = sys.version_info[0] >= 3

if PY3:
    from io import StringIO
    iteritems = operator.methodcaller("items")

else:
    from StringIO import StringIO
    iteritems = operator.methodcaller("iteritems")
