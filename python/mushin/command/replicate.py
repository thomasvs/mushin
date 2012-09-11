# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

from twisted.internet import defer
from twisted.web import error as twerror

from paisley import pjson as json

from mushin.extern.log import log

from mushin.common import logcommand, tcommand

HOST = 'localhost'
PORT = 5984
DB = 'mushin'

class Add(tcommand.TwistedCommand):
    summary = "Add another database to replicate with"
    usage = "REMOTE_HOST[:REMOTE_PORT][/REMOTE_DB]"

    @defer.inlineCallbacks
    def doLater(self, args):

        c = self.getRootCommand()

        # FIXME: parse with a proper library, could also include auth
        try:
            jane = args[0]
        except IndexError:
            self.stdout.write('Please give a database to replicate with.\n')
            return

        db = DB
        slash = jane.find('/')
        if slash > -1:
            db = jane[slash + 1:]
            jane = jane[:slash]
            self.debug('replicating to database %s', db)

        port = PORT
        colon = jane.find(':')
        if colon > -1:
            port = int(jane[colon + 1:])
            jane = jane[:colon]
            self.debug('replicating to port %d', port)

        dbs = [
          c.dbName,
          "http://%s:%d/%s" % (jane, port, db),
        ]

        server = c.getNewServer()
        # FIXME: don't poke privately
        client = server._couch

        for source, target in [(dbs[0], dbs[1]), (dbs[1], dbs[0])]:
            s = json.dumps({
              "source": source,
              "target": target,
              "continuous": True})
            self.info('replicating from %s to %s', source, target)
            self.debug('json string: %s', s)
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
                            source.encode('utf-8'), target.encode('utf-8')))
                    else:
                        error = r
                except Exception, e:
                    error = 'Exception: %r\n' % e

            if error:
                self.stdout.write('- Failed to replicate %s to %s:\n' % (
                    source.encode('utf-8'), target.encode('utf-8')))
                self.stdout.write('  %s\n' % error)

class Replicate(logcommand.LogCommand):
    description = """Manage replication.
"""

    subCommandClasses = [Add, ]
