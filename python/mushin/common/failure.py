# -*- Mode: Python; test-case-name: mushin.test.test_common_failure -*-
# vi:si:et:sw=4:sts=4:ts=4

from twisted.python import failure as tfailure

def getAllTracebacks(failure):
    """
    Return a list of all tracebacks of all nested failures and exceptions.
    """

    ret = []
    ret.append(failure.getTraceback())

    # some failures, like
    # twisted.web._newclient.RequestGenerationFailed,
    # are exceptions with multiple exceptions in them
    if isinstance(failure.value, Exception):
        for arg in failure.value.args:
            if isinstance(arg, list):
                ret.extend([getAllTracebacks(f) for f in arg])
            elif isinstance(arg, tfailure.Failure):
                ret.append(arg.getTraceback())

    return "\n".join(ret)
