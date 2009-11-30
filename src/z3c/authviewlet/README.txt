Login and logout
----------------

Login and logout work both for basic auth and cookie auth.


Setup
~~~~~

The layout page template has to include two content providers (viewlet
mangers):

  - ``login-logout-head`` inside the head tag to get automatic
    redirects and JavaScript code which does the logout for basic
    auth and

  - ``login-logout`` inside the body tag to get login and logout links.

The sample template looks like this:

  >>> import os.path
  >>> template_path = os.path.join(os.path.dirname(__file__), "tests",
  ...     "login-logout-template.pt")
  >>> print file(template_path, "r").read()
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
      <tal:block replace="structure provider:login-logout-head" />
    </head>
    <body>
      <tal:block replace="structure provider:login-logout" />
      <tal:block replace="structure provider:pagelet" />
    </body>
  </html>

This template is registered for the ``IContainer`` interface in
``ftesting.zcml``. After creating a container the template is
used when browsing the container:

  >>> from zope.container.btree import BTreeContainer
  >>> getRootFolder()['container'] = BTreeContainer()

Basic auth
~~~~~~~~~~

When the user is not logged in the login link is displayed:

  >>> from zope.testbrowser.testing import Browser
  >>> skinURL = 'http://localhost/++skin++PageletTestSkin/'
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open(skinURL + 'container/@@default.html')
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">Login</a>
    </body>
  </html>

Selecting the link leads to the login page, as we use basic auth here,
we get an HTTP error 401 (unauthorized):

  >>> login_url = browser.getLink('Login').url
  >>> browser.getLink('Login').click()
  Traceback (most recent call last):
  httperror_seek_wrapper: HTTP Error 401: Unauthorized
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html'

When adding correct credentials we get authorized:

  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.reload()

We are redirected to the page where we selected the login link. After
logging in the login link is no longer displayed. As we did not
specify that logout is supported, no logout link is displayed:

  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
    </body>
  </html>

Calling the login URL again leads directly to the page referred in nextURL:

  >>> browser.open(login_url)
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
    </body>
  </html>

Calling the login URL again without the query parameter leeds to a
confirmation page telling that login was successfull:

  >>> browser.open(login_url.split('?')[0])
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@login.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    <div>
     <h1>Login successful!</h1>
     <p style="font-size: 200%"> You are now logged in as <em>Manager</em>. </p>
     <a href=".">Back to the main page.</a>
    </div>
  </body>
  </html>

Selecting the ``Back to the main page.`` link send the user back to
the default view of the container. (``ftesting.zcml`` defines
``@@default.html`` as the default view.):

  >>> browser.getLink('Back to the main page.').click()
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
    </body>
  </html>


Providing an ``ILogoutSupported`` adapter leads to a logout link being
displayed:

  >>> from zope.app.testing import ztapi
  >>> import zope.interface
  >>> import zope.authentication.logout
  >>> import zope.authentication.interfaces
  >>> ztapi.provideAdapter(
  ...     zope.interface.Interface,
  ...     zope.authentication.interfaces.ILogoutSupported,
  ...     zope.authentication.logout.LogoutSupported)
  >>> browser.reload()
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@logout.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">Logout</a>
    </body>
  </html>

Logout is done using JavaScript and a redirect. zope.testbrowser
follows the redirects even if they use the meta tag instead of the
status code. So I have to use a non API call to change this behavior
to show the file contents:

  >>> browser.mech_browser.set_handle_refresh(False)

As testbrowser is not able to execute JavaScript the user remains
authenticated:

  >>> logout_url = browser.getLink('Logout').url
  >>> browser.getLink('Logout').click()
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@logout.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
      <script type="text/javascript"><!--
    // clear HTTP Authentication
    ...
    //-->
  </script>
  <meta http-equiv="refresh"
        content="0;url=http://localhost/++skin++PageletTestSkin/container/@@default.html" />
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@logout.html/@@logout.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40logout.html">Logout</a>
      <div>
    <h1>You are being redirected!</h1>
    <p style="font-size: 150%">
      <a href="http://localhost/++skin++PageletTestSkin/container/@@default.html">
        If you see this screen for more than 5 seconds, click here.
      </a>
    </p>
  </div>
    </body>
  </html>

Calling the logout URL again after logout (simulated using a new
browser instance) leads directly to the page referred in nextURL:

  >>> browser2 = Browser(logout_url)
  >>> browser2.url
  'http://localhost/++skin++PageletTestSkin/container/@@default.html'
  >>> print browser2.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">Login</a>
    </body>
  </html>

Calling the logout URL again without the query parameter leeds to a
confirmation page telling that logout was successfull:

  >>> browser2.open(logout_url.split('?')[0])
  >>> browser2.url
  'http://localhost/++skin++PageletTestSkin/container/@@logout.html'
  >>> print browser2.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
      <script type="text/javascript"><!--
    // clear HTTP Authentication
    ...
    //-->
  </script>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/logout.html/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40logout.html">Login</a>
      <div>
    <h1>Logout successful!</h1>
    <p style="font-size: 200%">
      You are now logged out.
    </p>
    <a href=".">Back to the main page.</a>
  </div>
    </body>
  </html>


Cookie auth
~~~~~~~~~~~

To do cookie auth we have to set up a pluggable auth utility (PAU)
with a authenticator plug-in (principal folder) first:

  >>> from zope.authentication.interfaces import IAuthentication
  >>> from zope.app.authentication.interfaces import IAuthenticatorPlugin
  >>> from zope.app.authentication.authentication import PluggableAuthentication
  >>> from zope.app.authentication.principalfolder import PrincipalFolder
  >>> from zope.site import site

  >>> root = getRootFolder()
  >>> root['principal_folder'] = PrincipalFolder()
  >>> sm = root.getSiteManager()
  >>> sm.registerUtility(
  ...     root['principal_folder'], IAuthenticatorPlugin, 'principal_folder')

  >>> root['auth'] = PluggableAuthentication()
  >>> sm.registerUtility(root['auth'], IAuthentication, '')
  >>> root['auth'].credentialsPlugins = (u'Session Credentials',)
  >>> root['auth'].authenticatorPlugins = (u'principal_folder',)

We need a principal inside the principal folder:

  >>> from zope.app.authentication.principalfolder import InternalPrincipal
  >>> root['principal_folder']['1'] = InternalPrincipal(
  ...     'tester', 'tpass', 'Tester')


We use a new browser, so the principal is not logged in and the login
link is displayed:

  >>> browser = Browser()
  >>> browser.open(skinURL + 'container/@@default.html')
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">Login</a>
    </body>
  </html>

Selecting the link leads to the login page:

  >>> login_url = browser.getLink('Login').url
  >>> browser.getLink('Login').click()
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/@@loginForm.html?camefrom=%2F%2B%2Bskin%2B%2BPageletTestSkin%2Fcontainer%2F%40%40login.html%3FnextURL%3Dhttp%253A%2F%2Flocalhost%2F%252B%252Bskin%252B%252BPageletTestSkin%2Fcontainer%2F%2540%2540default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    <div>
    <p>
      Please provide Login Information
    </p>
    <form action="" method="post">
      <div class="row">
        <div class="label"><label for="login">User Name</label></div>
        <div class="field">
          <input type="text" name="login" id="login" />
        </div>
      </div>
      <div class="row">
        <div class="label"><label for="password">Password</label></div>
        <div class="field">
          <input type="password" name="password" id="password" />
        </div>
      </div>
      <div class="row">
        <input class="form-element" type="submit"
               name="SUBMIT" value="Log in" />
      </div>
      <input type="hidden" name="camefrom"
             value="/++skin++PageletTestSkin/container/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">
    </form>
  </div>
  </body>
  </html>

Entering wrong username does not authorize but display an error
message:

  >>> browser.getControl('User Name').value = 'me'
  >>> browser.getControl('Password').value = 'tpass'
  >>> browser.getControl('Log in').click()
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/@@loginForm.html?camefrom=%2F%2B%2Bskin%2B%2BPageletTestSkin%2Fcontainer%2F%40%40login.html%3FnextURL%3Dhttp%253A%2F%2Flocalhost%2F%252B%252Bskin%252B%252BPageletTestSkin%2Fcontainer%2F%2540%2540default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    <div>
    <p>
      Please provide Login Information
    </p>
    <form action="" method="post">
      <div class="row">
        <div class="label"><label for="login">User Name</label></div>
        <div class="field">
          <input type="text" name="login" id="login" />
        </div>
      </div>
      <div class="row">
        <div class="label"><label for="password">Password</label></div>
        <div class="field">
          <input type="password" name="password" id="password" />
        </div>
      </div>
      <div class="row">
        <input class="form-element" type="submit"
               name="SUBMIT" value="Log in" />
      </div>
      <input type="hidden" name="camefrom"
             value="/++skin++PageletTestSkin/container/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">
    </form>
  </div>
  </body>
  </html>

Entering wrong password does not authorize either:

  >>> browser.getControl('User Name').value = 'tester'
  >>> browser.getControl('Password').value = 'let me in'
  >>> browser.getControl('Log in').click()
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/@@loginForm.html?camefrom=%2F%2B%2Bskin%2B%2BPageletTestSkin%2Fcontainer%2F%40%40login.html%3FnextURL%3Dhttp%253A%2F%2Flocalhost%2F%252B%252Bskin%252B%252BPageletTestSkin%2Fcontainer%2F%2540%2540default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    <div>
    <p>
      Please provide Login Information
    </p>
    <form action="" method="post">
      <div class="row">
        <div class="label"><label for="login">User Name</label></div>
        <div class="field">
          <input type="text" name="login" id="login" />
        </div>
      </div>
      <div class="row">
        <div class="label"><label for="password">Password</label></div>
        <div class="field">
          <input type="password" name="password" id="password" />
        </div>
      </div>
      <div class="row">
        <input class="form-element" type="submit"
               name="SUBMIT" value="Log in" />
      </div>
      <input type="hidden" name="camefrom"
             value="/++skin++PageletTestSkin/container/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">
    </form>
  </div>
  </body>
  </html>


After entering a correct username and password the user gets
authorized:

  >>> browser.getControl('User Name').value = 'tester'
  >>> browser.getControl('Password').value = 'tpass'
  >>> browser.getControl('Log in').click()

The user gets redirected to the page where he selected the login
link. After logging in the login link is no longer displayed. As we
already specified that logout is supported, a logout link is
displayed:

  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@logout.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">Logout</a>
    </body>
  </html>


Calling the login URL again leads directly to the page referred in nextURL:

  >>> browser.open(login_url)
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@logout.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">Logout</a>
    </body>
  </html>

Calling the login URL again without the query parameter leeds to a
confirmation page telling that login was successfull:

  >>> browser.open(login_url.split('?')[0])
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@login.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    <div>
     <h1>Login successful!</h1>
     <p style="font-size: 200%"> You are now logged in as <em>Tester</em>. </p>
     <a href=".">Back to the main page.</a>
    </div>
  </body>
  </html>

Selecting the ``Back to the main page.`` link send the user back to
the default view of the container. (``ftesting.zcml`` defines
``@@default.html`` as the default view.):

  >>> browser.getLink('Back to the main page.').click()
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@logout.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">Logout</a>
    </body>
  </html>


Selecting the displayed logout link drops authentication information
and displays a confirmation page, which redirects to the default page
where the login link is displayed again (as redirection is done
automatically by testbrowser I have to use the non API call trick
again to show the displayed page):

  >>> browser.mech_browser.set_handle_refresh(False)
  >>> logout_url = browser.getLink('Logout').url
  >>> browser.getLink('Logout').click()
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
      <script type="text/javascript"><!--
    // clear HTTP Authentication
    ...
    //-->
  </script>
  <meta http-equiv="refresh"
        content="0;url=http://localhost/++skin++PageletTestSkin/container/@@default.html" />
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@logout.html/@@logout.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40logout.html">Logout</a>
      <div>
    <h1>You are being redirected!</h1>
  <BLANKLINE>
    <p style="font-size: 150%">
      <a href="http://localhost/++skin++PageletTestSkin/container/@@default.html">
        If you see this screen for more than 5 seconds, click here.
      </a>
    </p>
  </div>
    </body>
  </html>
  >>> browser.getLink('If you see this screen for more than 5 seconds').click()
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">Login</a>
    </body>
  </html>
  >>> browser.mech_browser.set_handle_refresh(True)

Calling the logout URL again after logout leads directly to the page
referred in nextURL:

  >>> browser.open(logout_url)
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@default.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40default.html">Login</a>
    </body>
  </html>

Calling the logout URL again without the query parameter leeds to a
confirmation page telling that logout was successfull:

  >>> browser.open(logout_url.split('?')[0])
  >>> browser.url
  'http://localhost/++skin++PageletTestSkin/container/@@logout.html'
  >>> print browser.contents
  <!DOCTYPE ...>
  <html ...>
    <head>
      <title>PageletTest</title>
      <script type="text/javascript"><!--
    // clear HTTP Authentication
    ...
    //-->
  </script>
    </head>
    <body>
      <a href="http://localhost/++skin++PageletTestSkin/container/logout.html/@@login.html?nextURL=http%3A//localhost/%2B%2Bskin%2B%2BPageletTestSkin/container/%40%40logout.html">Login</a>
      <div>
    <h1>Logout successful!</h1>
    <p style="font-size: 200%">
      You are now logged out.
    </p>
    <a href=".">Back to the main page.</a>
  </div>
    </body>
  </html>
