##############################################################################
#
# Copyright (c) 2003-2009 Zope Foundation and Contributors.
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

"""Login and logout viewlets."""
import urllib.parse

import z3c.pagelet.interfaces
import zope.authentication.interfaces
import zope.component
import zope.i18n
import zope.i18nmessageid
import zope.interface
import zope.viewlet.interfaces
import zope.viewlet.manager
import zope.viewlet.viewlet

import z3c.authviewlet.interfaces


_ = zope.i18nmessageid.MessageFactory("z3c")


class ILoginLogoutHeadViewletManager(zope.viewlet.interfaces.IViewletManager):
    """ViewletManager for supporting header contents (e. g. JavaScript)."""


LoginLogoutHeadViewletManager = zope.viewlet.manager.ViewletManager(
    'login-logout-head', ILoginLogoutHeadViewletManager)


class ILoginLogoutViewletManager(zope.viewlet.interfaces.IViewletManager):
    """ViewletManager for login and logout viewlets."""


LoginLogoutViewletManager = zope.viewlet.manager.ViewletManager(
    'login-logout', ILoginLogoutViewletManager,
    bases=(zope.viewlet.manager.ConditionalViewletManager,))


def authenticated(principal):
    "Tell whether the principal is authenticated."
    unauthenticated = zope.authentication.interfaces.IUnauthenticatedPrincipal
    return not unauthenticated.providedBy(principal)


def logout_supported(request):
    "Tell whether logout is supported."
    logout = zope.authentication.interfaces.ILogoutSupported(request, None)
    return logout is not None


def get_view_url(context, request, view_name):
    "Compute the url of a view."
    if view_name.startswith('@@'):
        view_name = view_name[2:]
        view_name_truncated = True
    else:
        view_name_truncated = False
    view = zope.component.getMultiAdapter((context, request), name=view_name)
    view_url = zope.component.getMultiAdapter(
        (view, request), name='absolute_url')()
    if view_name_truncated:
        view_url = view_url.replace(view_name, '@@' + view_name)
    return view_url


def render_pagelet(context, request, view_name):
    "Render a pagelet."
    pagelet = zope.component.getMultiAdapter(
        (context, request), z3c.pagelet.interfaces.IPagelet, name=view_name)
    return pagelet()


class LoginViewlet(zope.viewlet.viewlet.ViewletBase):
    """Display login link when user is not logged in."""

    @property
    def available(self):
        return not authenticated(self.request.principal)

    def render(self):
        return '<a href="{}?nextURL={}">{}</a>'.format(
            get_view_url(self.context, self.request, self.viewName),
            urllib.parse.quote(self.request.getURL()),
            zope.i18n.translate(_('[Login]', default='Login'),
                                domain='z3c', context=self.request))


class LogoutViewlet(zope.viewlet.viewlet.ViewletBase):
    """Display logout link when user is logged in and logout is supported."""

    @property
    def available(self):
        return (
            authenticated(self.request.principal)
            and
            logout_supported(self.request))

    def render(self):
        return '<a href="{}?nextURL={}">{}</a>'.format(
            get_view_url(self. context, self.request, self.viewName),
            urllib.parse.quote(self.request.getURL()),
            zope.i18n.translate(_('[Logout]', default='Logout'),
                                domain='z3c',
                                context=self.request))


@zope.interface.implementer(z3c.authviewlet.interfaces.ILogin)
class HTTPAuthenticationLogin:

    def login(self, nextURL=None):
        # we don't want to keep challenging if we're authenticated
        if not authenticated(self.request.principal):
            auth = zope.component.getUtility(
                zope.authentication.interfaces.IAuthentication)
            auth.unauthorized(
                self.request.principal.id, self.request)
            return render_pagelet(self, self.request, 'login_failed.html')
        else:
            if nextURL is None:
                return render_pagelet(self, self.request, 'login_success.html')
            else:
                self.request.response.redirect(nextURL)


class LoginFailedPagelet:
    "Pagelet to display login failed notice."


class LoginSuccessfulPagelet:
    "Pagelet to display login succecc notice."


@zope.interface.implementer(zope.authentication.interfaces.ILogout)
class HTTPAuthenticationLogout:
    """Since HTTP Authentication really does not know about logout, we are
    simply challenging the client again."""

    def logout(self, nextURL=None):
        if authenticated(self.request.principal):
            auth = zope.component.getUtility(
                zope.authentication.interfaces.IAuthentication)
            zope.authentication.interfaces.ILogout(auth).logout(self.request)
            if nextURL:
                return render_pagelet(self, self.request, 'redirect.html')
        if nextURL is None:
            return render_pagelet(self, self.request, 'logout_success.html')
        else:
            return self.request.response.redirect(nextURL)


class LogoutRedirectPagelet:
    "Pagelet to display logout redirect."


class LogoutSuccessPagelet:
    "Pagelet to display logout success."
