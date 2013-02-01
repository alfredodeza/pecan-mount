import httputil
from pecan import request
from pecan.core import Pecan as PecanApplication
from pecan_mount._compat import native_to_unicode, py3k
from pecan_mount.util import downgrade_wsgi_ux_to_1x


class MountMiddleware(object):

    def __init__(self, root, application, script_name, configuration=None):
        self.root = root # root app
        self.application = application
        self.configuration = configuration # what
        self.script_name = script_name # do not allow ""

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.script_name):
            return self.application(environ, start_response)
        return self.root(environ, start_response)


class Tree(object):
    """
    A registry of Pecan applications, mounted at diverse points.

    An instance of this class may also be used as a WSGI callable
    (WSGI application object), in which case it dispatches to all
    mounted apps.

    .. attribute:: apps
    A dict of the form {script name: application}, where "script name" is
    a string declaring the URI mount point (no trailing slash), and
    "application" is an instance of pecan.Application (or an arbitrary WSGI
    callable if you happen to be using a WSGI server).
    """

    def __init__(self):
        self.apps = {}

    def mount(self, root, script_name="", config=None):
        """Mount a new app from a root object, script_name, and config.

        root
            An instance of a "controller class" (a collection of page
            handler methods) which represents the root of the application.
            This may also be an Application instance, or None if using
            a dispatcher other than the default.

        script_name
            A string containing the "mount point" of the application.
            This should start with a slash, and be the path portion of the
            URL at which to mount the given root. For example, if root.index()
            will handle requests to "http://www.example.com:8080/dept/app1/",
            then the script_name argument would be "/dept/app1".

            It MUST NOT end in a slash. If the script_name refers to the
            root of the URI, it MUST be an empty string (not "/").

        config
            A file or dict containing application config.
        """
        if script_name is None:
            raise TypeError(
                "The 'script_name' argument may not be None. Application "
                "objects may, however, possess a script_name of None (in "
                "order to inpect the WSGI environ for SCRIPT_NAME upon each "
                "request). You cannot mount such Applications on this Tree; "
                "you must pass them to a WSGI server interface directly.")

        # Next line both 1) strips trailing slash and 2) maps "/" -> "".
        script_name = script_name.rstrip("/")

        if isinstance(root, PecanApplication):
            app = root
            if script_name != "" and script_name != app.script_name:
                raise ValueError("Cannot specify a different script name and "
                                 "pass an Application instance to pecan.mount")
            script_name = app.script_name
        else:
            from pecan.core import load_app
            app = load_app(config)
            app.script_name = script_name

        if config:
            app.merge(config)

        self.apps[script_name] = app

        return app

    def graft(self, wsgi_callable, script_name=""):
        """Mount a wsgi callable at the given script_name."""
        # Next line both 1) strips trailing slash and 2) maps "/" -> "".
        script_name = script_name.rstrip("/")
        self.apps[script_name] = wsgi_callable

    def script_name(self, path=None):
        """The script_name of the app at the given path, or None.

        If path is None, pecan.request is used.
        """
        if path is None:
            try:
                # FIXME pecan requests don't have these attributes
                path = httputil.urljoin(request.script_name,
                                        request.path_info)
            except AttributeError:
                return None

        while True:
            if path in self.apps:
                return path

            if path == "":
                return None

            # Move one node up the tree and try again.
            path = path[:path.rfind("/")]

    def __call__(self, environ, start_response):
        # If you're calling this, then you're probably setting SCRIPT_NAME
        # to '' (some WSGI servers always set SCRIPT_NAME to '').
        # Try to look up the app using the full path.
        env1x = environ
        if environ.get(native_to_unicode('wsgi.version')) == (native_to_unicode('u'), 0):
            env1x = downgrade_wsgi_ux_to_1x(environ)
        path = httputil.urljoin(env1x.get('SCRIPT_NAME', ''),
                                env1x.get('PATH_INFO', ''))
        sn = self.script_name(path or "/")
        if sn is None:
            start_response('404 Not Found', [])
            return []

        app = self.apps[sn]

        # Correct the SCRIPT_NAME and PATH_INFO environ entries.
        environ = environ.copy()
        if not py3k:
            if environ.get(native_to_unicode('wsgi.version')) == (native_to_unicode('u'), 0):
                # Python 2/WSGI u.0: all strings MUST be of type unicode
                enc = environ[native_to_unicode('wsgi.url_encoding')]
                environ[native_to_unicode('SCRIPT_NAME')] = sn.decode(enc)
                environ[native_to_unicode('PATH_INFO')] = path[len(sn.rstrip("/")):].decode(enc)
            else:
                # Python 2/WSGI 1.x: all strings MUST be of type str
                environ['SCRIPT_NAME'] = sn
                environ['PATH_INFO'] = path[len(sn.rstrip("/")):]
        else:
            if environ.get(native_to_unicode('wsgi.version')) == (native_to_unicode('u'), 0):
                # Python 3/WSGI u.0: all strings MUST be full unicode
                environ['SCRIPT_NAME'] = sn
                environ['PATH_INFO'] = path[len(sn.rstrip("/")):]
            else:
                # Python 3/WSGI 1.x: all strings MUST be ISO-8859-1 str
                environ['SCRIPT_NAME'] = sn.encode('utf-8').decode('ISO-8859-1')
                environ['PATH_INFO'] = path[len(sn.rstrip("/")):].encode('utf-8').decode('ISO-8859-1')
        return app(environ, start_response)
