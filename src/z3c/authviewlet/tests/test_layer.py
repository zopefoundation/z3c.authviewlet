import doctest
import re

import zope.app.wsgi.testlayer
from zope.testing import renormalizing

import z3c.authviewlet


TestLayer = zope.app.wsgi.testlayer.BrowserLayer(z3c.authviewlet)
checker = renormalizing.RENormalizing([
    (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
    (re.compile(r'urllib.error.HTTPError:', re.M), 'HTTPError:'),
])
flags = (
    doctest.ELLIPSIS |
    doctest.REPORT_UDIFF |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_ONLY_FIRST_FAILURE
)


def test_suite():
    suite = doctest.DocFileSuite(
        '../README.txt', checker=checker, optionflags=flags,
        globs={'layer': TestLayer})
    suite.layer = TestLayer
    return suite
