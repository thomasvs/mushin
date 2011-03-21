# -*- Mode: Python; test-case-name: mushin.test.test_common_parse -*-
# vi:si:et:sw=4:sts=4:ts=4

import unittest

from mushin.common import parse

class ParseTestCase(unittest.TestCase):
    def testWeek(self):
        d = parse.parse(u"R:1W")
        self.assertEquals(d['recurrence'], 60 * 60 * 24 * 7)
