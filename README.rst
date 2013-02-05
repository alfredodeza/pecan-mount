
Pecan Mount
===========
A utility to mount Pecan applications at different points to act as one.


Adding applications
-------------------
Pecan applications are usually mounted at `/` and they do not have an easy way
to be able to compound different apps working in unison. If you are using
`pecan_mount` you need to use the tree as the actual WSGI application as it
acts as WSGI middleware to properly return the apps at given mount points.

You only need two things for mounting an app, an application configuration and
the mount point. The configuration can be either a path to a file or
a dictionary (Pecan takes care of this loading for us). So to mount a single
application at `/application` with a configuration file living in
`/path/to/config.py` it would look like this::

    import pecan_mount
    pecan_mount.tree.mount('/application', '/path/to/config.py')

The nice things about Pecan configuration is that it will take care of finding
the right modules and everything necessary for your application. At most, the
important decision here is the mount point.


Running multiple applications
----------------------------
Ideally, you would want to mount all the applications you need in one place,
and this place should be where the WSGI application is constructed so that it
can be consumed by a WSGI server (for example `gunicorn` or Apache with
`mod_wsgi`). This is how having 4 different applications would look in a file
called `wsgi.py`::

    import pecan_mount

    pecan_mount.tree.mount('/', '/path/to/main_config.py')
    pecan_mount.tree.mount('/admin', '/path/to/admin_config.py')
    pecan_mount.tree.mount('/registration', '/path/to/registration_config.py')
    pecan_mount.tree.mount('/_metrics', '/path/to/metrics_config.py')

    application = pecan_mount.tree 


Naming the mounts
-----------------
Optionally, when mounting, you can pass in a ``mount_name`` that will be used
added to the WSGI app as an attribute. This is useful when debugging or when
you need to have a better representation of what application is mounted at some
point.

If no ``mount_name`` is passed in to the ``mount`` callable, it will default to
inferring the name from the ``script_name``, which in turn will use ``root``
for empty strings or None and for dotted conversions for other paths.

For example, a ``script_name`` that looks like: ``/foo/bar`` will be translated
to a ``mount_name`` of ``foo.bar``.


Preventing overriding of mounts
-------------------------------
The ``tree`` object will prevent you from mounting applications in locations
where there is already an app mounted. This is convenient when there are
multiple applications mounted and unknowingly a new app is using a location
already taken. An ``AttributeError`` will be raised to indicate what
application at what mount point is being used and prevent further execution.


Mounting other WSGI apps
------------------------
Other WSGI applications can also be mounted easily. The WSGI app will need to
be properly configured before mounting and will use a different callable::

    import pecan_mount
    import my_app
    
    my_wsgi_app = my_app()

    pecan_mount.tree.graft(my_app, '/mount_point')
