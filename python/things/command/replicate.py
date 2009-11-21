# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

from things.common import logcommand

class Add(logcommand.LogCommand):
    summary = "Add another database to replicate with"
    usage = "[host]"

    def do(self, args):
        import httplib
        import cjson as json
        import codecs

        conn = httplib.HTTPConnection('localhost:5984')

        dbs = [
          "gtd",
          "http://%s:5984/gtd" % args[0],
        ]

        for source, target in [(dbs[0], dbs[1]), (dbs[1], dbs[0])]:
            s = json.encode({
              "source": source,
              "target": target,
              "continuous": True})
            self.debug('json string: %s', s)
            conn.request('POST', '/_replicate', s,
                {"Content-Type": "application/json"})
            try:
                r = conn.getresponse()
            except httplib.ResponseNotReady:
                print 'FAILED: local server failed for source %s' % source
                return

            if r.status / 100 == 2:
                print json.decode(r.read())
            else:
                print 'FAILED: status code', r.status
                return

class Replicate(logcommand.LogCommand):
    description = """Manage replication.
"""

    subCommandClasses = [Add, ]
