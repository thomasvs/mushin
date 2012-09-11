# -*- Mode: Python; test-case-name: mushin.test.test_common_urlrewrite -*-
# vi:si:et:sw=4:sts=4:ts=4

import unittest

from mushin.common import urlrewrite


class RewriteTestCase(unittest.TestCase):

    def testNoRewrite(self):
        url = urlrewrite.rewrite('http://localhost:80', hostname='localhost')
        self.assertEquals(url, 'http://localhost:80')

    def testDefaultHost(self):
        url = urlrewrite.rewrite('http://:80', hostname='localhost')
        self.assertEquals(url, 'http://localhost:80')

    def testDefaultUsername(self):
        url = urlrewrite.rewrite('http://:80', hostname='localhost',
            username='thomas')
        self.assertEquals(url, 'http://thomas:@localhost:80')

    def testNoRewriteAll(self):
        orig = 'http://username:password@ana:5985/mushint'
        url = urlrewrite.rewrite(orig,
            hostname='localhost', port=5984,
            username='thomas', password='test',
            path='/mushin')
        self.assertEquals(url, orig)

    def testRewriteAll(self):
        orig = 'http://'
        url = urlrewrite.rewrite(orig,
            hostname='localhost', port=5984,
            username='thomas', password='test',
            path='/mushin')
        self.assertEquals(url, 'http://thomas:test@localhost:5984/mushin')


class RewriteSafeCase(unittest.TestCase):

    def testRewriteSafe(self):
        url = urlrewrite.rewrite_safe(
            'http://thomas:test@localhost:5984/mushin')
        self.assertEquals(url, 'http://thomas:****@localhost:5984/mushin')
