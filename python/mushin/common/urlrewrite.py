# -*- Mode: Python; test-case-name: mushin.test.test_common_urlrewrite -*-
# vi:si:et:sw=4:sts=4:ts=4

import urlparse

def _netloc(hostname, port, username=None, password=None):
    netloc = hostname
    if port:
        netloc += ':' + str(port)

    if username or password:
        netloc = '%s:%s@%s' % (username, password, netloc)

    return netloc



def rewrite(url, hostname=None, port=None, username=None, password=None,
        path=None):
    """
    Rewrite the given URL, overriding with the given defaults.
    """
    parsed = urlparse.urlparse(url)

    password = parsed.password or password or ''

    parsed = parsed._replace(netloc=_netloc(
        parsed.hostname or hostname,
        parsed.port or port,
        parsed.username or username or '',
        password
        ))

    if not parsed.path and path:
        parsed = parsed._replace(path=path)

    return parsed.geturl()

def rewrite_safe(url):
    """
    Rewrite the given URL, replacing the password with asterisks.
    """
    parsed = urlparse.urlparse(url)

    password = '*' * len(parsed.password or '')

    parsed = parsed._replace(netloc=_netloc(
        parsed.hostname,
        parsed.port,
        parsed.username,
        password
        ))

    return parsed.geturl()


