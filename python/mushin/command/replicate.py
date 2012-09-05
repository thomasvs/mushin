# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

from mushin.common import logcommand

HOST = 'localhost'
PORT = 5984
DB = 'mushin'

class Add(logcommand.LogCommand):
    summary = "Add another database to replicate with"
    usage = "REMOTE_HOST[:REMOTE_PORT][/REMOTE_DB]"

    def do(self, args):
        import socket
        import httplib
        import cjson as json

        c = self.getRootCommand()
        # FIXME: this hardcodes our own port/server
        conn = httplib.HTTPConnection('%s:%d' % (c.host, c.port))

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

        for source, target in [(dbs[0], dbs[1]), (dbs[1], dbs[0])]:
            s = json.encode({
              "source": source,
              "target": target,
              "continuous": True})
            self.debug('json string: %s', s)
            try:
                conn.request('POST', '/_replicate', s,
                    {"Content-Type": "application/json"})
            except socket.error:
                self.stdout.write('FAILED: local server failed for source %s\n' % source)
                self.stdout.write('Is the server running ?\n')
                return
            try:
                r = conn.getresponse()
            except httplib.ResponseNotReady:
                self.stdout.write('FAILED: local server failed for source %s\n' % source)
                return

            if r.status / 100 == 2:
                self.stdout.write("%r\n" % json.decode(r.read()))
            else:
                self.stdout.write('FAILED: status code %r\n' % r.status)
                return

class Replicate(logcommand.LogCommand):
    description = """Manage replication.
"""

    subCommandClasses = [Add, ]
