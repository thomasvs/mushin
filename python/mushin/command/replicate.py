# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

from mushin.common import logcommand

class Add(logcommand.LogCommand):
    summary = "Add another database to replicate with"
    usage = "[host]"

    def do(self, args):
        import socket
        import httplib
        import cjson as json
        import codecs

        # FIXME: this hardcodes our own port/server
        conn = httplib.HTTPConnection('localhost:5984')

        try:
            jane = args[0]
        except IndexError:
            self.stdout.write('Please give a database to replicate with.\n')
            return

        if ':' not in jane:
            jane += ':5984'

        dbs = [
          "mushin",
          "http://%s/mushin" % jane,
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
            except socket.error, e:
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
