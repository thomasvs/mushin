# -*- Mode: Python; test-case-name: mushin.test.test_common_failure -*-
# vi:si:et:sw=4:sts=4:ts=4


import unittest

from twisted.python import failure as tfailure
from twisted.web import _newclient as client

from mushin.common import failure

class FailureTestCase(unittest.TestCase):
    def testSynthetic(self):
        e = client.RequestGenerationFailed([
            tfailure.Failure(ValueError()),
        ])
        f = tfailure.Failure(e)
        print failure.getAllTracebacks(f)
