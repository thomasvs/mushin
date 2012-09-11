# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import urlparse

from twisted.internet import defer
from twisted.web import error as twerror

from paisley import pjson as json

from mushin.extern.log import log

from mushin.common import logcommand, tcommand, urlrewrite

HOST = 'localhost'
PORT = 5984
DB = 'mushin'

class Add(tcommand.TwistedCommand):
    summary = "Add another database to replicate with"
    usage = "http://[USER[:PASSWORD]@]HOST[:PORT][/DB]"
    description = """Set up two-way replication with another database.

If you provide a username, but not a password, you will be prompted for
the remote password.

The default remote host is %s.
The default remote port is %d.
The default remote database is %s.
""" % (HOST, PORT, DB)
    

    @defer.inlineCallbacks
    def doLater(self, args):

        c = self.getRootCommand()

        try:
            url = args[0]
        except IndexError:
            self.stdout.write('Please give a database to replicate with.\n')
            return

        # if a username was given, but no password, ask for it
        parsed = urlparse.urlparse(url)
        password = None
        if parsed.username and not parsed.password:
            password = self.getRootCommand().getPassword(
                prompt='Password for %s: ' % url)


        jane = urlrewrite.rewrite(url, hostname=HOST, port=PORT,
            password=password, path='/' + DB)

        dbs = [
          c.dbName,
          jane,
        ]

        server = c.getNewServer()
        # FIXME: don't poke privately
        client = server._couch

        for source, target in [(dbs[0], dbs[1]), (dbs[1], dbs[0])]:
            s = json.dumps({
              "source": source,
              "target": target,
              "continuous": True})
            self.info('replicating from %s to %s',
                urlrewrite.rewrite_safe(source),
                urlrewrite.rewrite_safe(target))
            try:
                d = client.post('/_replicate', s)
            except Exception, e:
                self.stdout.write('Exception %r\n', e)
                self.stdout.write(
                    'FAILED: local server failed for source %s\n' %
                        source.encode('utf-8'))
                self.stdout.write('Is the server running ?\n')
                defer.returnValue(e)
                return

            error = None # set with a non-newline string in case of error

            try:
                result = yield d
            except twerror.Error, e:
                error = 'CouchDB returned error response %r' % e.status
                try:
                    r = json.loads(e.message)
                    error = 'CouchDB returned error reason: %s' % r['reason']
                except:
                    pass
            except:
                error = log.getExceptionMessage(e)

            if not error:
                r = json.loads(result)

                try:
                    if r['ok']:
                        self.stdout.write('+ Replicating %s to %s\n' % (
                            urlrewrite.rewrite_safe(source.encode('utf-8')),
                            urlrewrite.rewrite_safe(target.encode('utf-8'))))
                    else:
                        error = r
                except Exception, e:
                    error = 'Exception: %r\n' % e

            if error:
                self.stdout.write('- Failed to replicate %s to %s:\n' % (
                    urlrewrite.rewrite_safe(source.encode('utf-8')),
                    urlrewrite.rewrite_safe(target.encode('utf-8'))))
                self.stdout.write('  %s\n' % error)

class Replicate(logcommand.LogCommand):
    description = """Manage replication.
"""

    subCommandClasses = [Add, ]
