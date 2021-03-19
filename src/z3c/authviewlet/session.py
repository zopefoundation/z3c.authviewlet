##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Login Form."""
from zope.authentication.interfaces import IUnauthenticatedPrincipal

try:
    basestring
except NameError:  # pragma: PY3
    basestring = str


class SessionCredentialsLoginForm(object):
    """Login form using session credentials."""

    def __init__(self, *args):
        super(SessionCredentialsLoginForm, self).__init__(*args)
        self.unauthenticated = IUnauthenticatedPrincipal.providedBy(
            self.request.principal)

        camefrom = self.request.get('camefrom')
        assert isinstance(camefrom, basestring), type(camefrom)
        self.camefrom = camefrom

    def update(self):
        """Redirect when authenticated."""
        if (not self.unauthenticated) and ('SUBMIT' in self.request):
            # authenticated by submitting
            self.request.response.redirect(self.camefrom or '.')
