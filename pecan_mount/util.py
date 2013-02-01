

def downgrade_wsgi_ux_to_1x(environ):
    """Return a new environ dict for WSGI 1.x from the given WSGI u.x environ."""
    env1x = {}

    url_encoding = environ[native_to_unicode('wsgi.url_encoding')]
    for k, v in list(environ.items()):
        if k in [native_to_unicode('PATH_INFO'), native_to_unicode('SCRIPT_NAME'), native_to_unicode('QUERY_STRING')]:
            v = v.encode(url_encoding)
        elif isinstance(v, unicodestr):
            v = v.encode('ISO-8859-1')
        env1x[k.encode('ISO-8859-1')] = v

    return env1x



